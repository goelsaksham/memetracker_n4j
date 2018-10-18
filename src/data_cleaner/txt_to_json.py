import json
import os
import glob
from typing import List, TextIO


def exist_directory(directory_path: str):
    """
    This function checks whether a given path to a directory is valid. Returns a boolean value denoting whether the
    directory exist or not. Returns True if the given directory path exist, False otherwise.

    Args:
        :param directory_path: The path to the directory which is to be checked

    :return: True if the given path to the directory is valid (directory exist), False otherwise
    """
    return os.path.isdir(directory_path)


def exist_file(file_path: str):
    """
    This function checks whether a given path to a file is valid. Returns a boolean value denoting whether the
    file exist or not. Returns True if the given file path exist, False otherwise.

    Args:
        :param file_path: The path to the file which is to be checked

    :return: True if the given path to the file is valid (directory exist), False otherwise
    """
    return os.path.isfile(file_path)


def get_file_names(directory_path: str, file_extension: str) -> List[str]:
    """
    This function should is used to find the list of names of files present in a given directory which have the
    particular extension. Uses glob regular expression pattern matching to find the files with the given extension

    Args:
        :param directory_path: The path to the directory from which the names of the files with the particular
                               extension need to be extracted.
        :param file_extension: The extension for the files whose name will be returned. It is expected that this
                               argument will contain dot ('.') for better results.

    Returns:
        :return: A list of names of files that are present in the given directory and have the particular extension
    """
    # Initialize a list which will contain the names of the files with the given extension in the given directory,
    file_names = list()
    if not exist_directory(directory_path):
        print(f'The given directory path is invalid. Given: {directory_path}')
    else:
        # Getting the current working directory to save it
        process_cwd = os.getcwd()
        # Change the current working directory to the directory_path specified
        os.chdir(directory_path)
        # Get the names of the file with the given file_extension
        file_names = glob.glob(f'*{file_extension}')
        # Change the current working directory to the original working directory
        os.chdir(process_cwd)
    return file_names


def write_to_json_file(output_json_writer: TextIO, output_json_file_data: dict) -> None:
    """
    This function is responsible to write data to the JSON file.

    Args:
        :param output_json_writer: The file writer object for the JSON file.
        :param output_json_file_data: The data (dictionary) that will be written to the JSON file
                                      This dictionary is of the form:
                                      {
                                         meme_1_url: {
                                                'url': meme_1_url (P),
                                                'id_num': meme_1_id,
                                                'timestamp': meme_1_timestamp (T),
                                                'phrases': meme_1_phrases (Q),
                                                'links': meme_1_links (L)
                                                }
                                        .....
                                      }

    Returns:
        :return: None. Writes the dictionary object to the JSON file.
    """
    json.dump(output_json_file_data,
              output_json_writer,
              indent=4,     # Writes to JSON in a pretty format. Makes sure that each field is indented so that it is
                            # easy to visualize the data written to JSON file
              ensure_ascii=False)


def add_data_to_json_file_data_dict(individual_meme_data_dict: dict, output_json_file_data: dict,
                                    meme_record_id: int) -> None:
    """
    This function is responsible to add the data about a particular meme (article) extracted from the txt file to the
    dictionary containing data that would be written to the output JSON file.

    Args:
        :param individual_meme_data_dict: The dictionary representing all the data about an individual meme (article)
                                          which has been extracted from the input txt file. The format of the
                                          dictionary will be something like:
                                          {
                                            'P': url of the meme,
                                            'T': timestamp of the meme,
                                            'Q': important phrases extracted from the meme,
                                            'L': links present in the meme (to other memes)
                                          }

        :param output_json_file_data: The dictionary that contains all the data corresponding to each memes from the
                                      particular input txt file. This data will then be all written to the output
                                      JSON file.
                                      This dictionary is of the form:
                                      {
                                         meme_1_url: {
                                                'url': meme_1_url (P),
                                                'id_num': meme_1_id,
                                                'timestamp': meme_1_timestamp (T),
                                                'phrases': meme_1_phrases (Q),
                                                'links': meme_1_links (L)
                                                }
                                        .....
                                      }

        :param meme_record_id: The unique id for each meme (Article) record

    Returns:
        :return: None. Just adds the data about the current individual meme (article) to the JSON data dictionary in
                 the format required.
    """
    # Function used to unpack the data from the meme data dictionary
    def get_unpacked_data_from_record_data_dict():
        return individual_meme_data_dict['P'], individual_meme_data_dict['T'], individual_meme_data_dict['Q'], \
               individual_meme_data_dict['L']

    # Getting the unpacked data from the meme data dictionary
    url, timestamp, phrases, links = get_unpacked_data_from_record_data_dict()
    # Adding a record containing all the required data about this meme to the output_json_file_data dictionary
    output_json_file_data[url] = {
        'url': url,
        'id_num': meme_record_id,
        'timestamp': timestamp,
        'phrases': phrases,
        'links': links
    }


def construct_meme_data_tracker_dict() -> dict:
    """
    This function just returns a simple dictionary responsible to hold the data extracted from the input txt file for
    each individual meme. This function is used as an aggregator of the data until new meme record is encountered in
    the input txt file.

    Returns:
        :return: A dictionary which is responsible for holding the various attributes of an individual meme for which
                 the data is extracted from the input txt file.
    """
    return {
        'P': '',
        'T': '',
        'Q': [],
        'L': []
    }


def process_txt_file_line(file_line: str, individual_meme_data_dict: dict) -> bool:
    """
    This function is responsible to add data from a line of the input txt file to the dictionary aggregating data
    about an individual meme. Each file line is checked to see if it contains data about a particular meme (P, T,
    Q, L) or signifies a record (meme) change and adds the data accordingly. Returns a boolean value stating whether
    the currently line signifies a break (starting of a new record) or not.

    Args:
        :param file_line: An individual file line read from the file.
        :param individual_meme_data_dict: The dictionary that represents the aggregated data for the current meme.
                                          Data from the current line is added based on the identifier present at the
                                          start of the line. The dictionary is of the form:
                                          {
                                            'P': url of the meme,
                                            'T': timestamp of the meme,
                                            'Q': important phrases extracted from the meme,
                                            'L': links present in the meme (to other memes)
                                          }
    Returns:
        :return: True if the current line does not signify end of the current record (empty line), False otherwise.
    """
    # from datetime import datetime

    # Clear the line of any trailing whitespace or newline characters
    file_line = file_line.strip()
    # Get the initial letter of the line and the rest of the contents of the line
    try:
        # Split the string based on the tab character and unpack the two contents from each line.
        # The first content of the line should be the identifier for the line, which tells what kind of data
        # is being stored in the line, and the second part of the line should be the actual content
        # corresponding to the line.
        [content_identifier, line_content] = file_line.split('\t')
        if content_identifier in ['P', 'T']:
            individual_meme_data_dict[content_identifier] = line_content
            # Possibly add the suggestion of storing the information in datetime format.
            # individual_meme_data_dict[content_identifier] = datetime.strptime(line_content, '%Y-%m-%d %H:%M:%S')
        elif content_identifier in ['Q', 'L']:
            individual_meme_data_dict[content_identifier].append(line_content)
        else:
            print(f'Invalid line encountered in the file: {file_line}')
        return True
    except ValueError:  # If the line cannot be unpacked into two different items then the line is the breaker
        #  between different records. Use this to actually signify the function to save the data for this meme to the
        #  JSON data dictionary and reset the individual meme data dictionary.
        return False


def convert_txt_file_to_json(input_file_directory_path: str, input_txt_file_name: str, input_txt_file_extension: str,
                             output_json_directory_path: str, meme_record_id: int) -> int:
    """
    This function is responsible to load data about each individual meme from the input txt file and then store that
    data into the correct format into a JSON file.

    Args:
        :param input_file_directory_path: The path to the directory from where input txt files will be loaded
        :param input_txt_file_name: The name of the input txt file
        :param input_txt_file_extension: The extension for the input txt file
        :param output_json_directory_path: The directory where the output json file will be saved
        :param meme_record_id: The unique identifier for the current Meme (Article)

    Returns:
        :return: A number representing the unique id for the records from other files. This way we can use the value
                 returned by this function to start indexing the memes from other files and not have same id across
                 different files.
    """
    # import random
    # Construct the path to the input txt file from which data will be read
    input_txt_file_path = os.path.join(input_file_directory_path, input_txt_file_name)
    # Check if the file actually exist or not
    if not exist_file(input_txt_file_path):
        print(f'The path to the given input txt file is invalid. File Path: {input_txt_file_path}')
        return meme_record_id
    # Get the name of the JSON file by replacing the input file extension with .json
    output_json_file_name = input_txt_file_name.replace(input_txt_file_extension, '.json')
    # Construct the path to the output json file which will be populated with the data from the txt file
    output_json_file_path = os.path.join(output_json_directory_path, output_json_file_name)
    # Get the file writer object for the output json file
    output_json_writer = open(output_json_file_path, 'w')
    # Initialize the dictionary that will contain data about all the memes in the current txt file and then will be
    # written to the corresponding output JSON file
    output_json_file_data = dict()
    # Initialize the dictionary that will contain data about just individual memes. Used to aggregate data about
    # phrases and links until a new meme is encountered.
    individual_meme_data_dict = construct_meme_data_tracker_dict()
    with open(input_txt_file_path, encoding='utf-8') as txt_file:
        try:
            # Iterate through the file line by line
            for file_line in txt_file:
                # Process the particular file line and check whether it is time to reset the meme data dictionary
                # because a break is encountered (signifying end of previous and start of a new meme)
                if not process_txt_file_line(file_line, individual_meme_data_dict):
                    # Add the data about this meme to the JSON file data dictionary
                    add_data_to_json_file_data_dict(individual_meme_data_dict, output_json_file_data, meme_record_id)
                    # Reset the dictionary for the meme data aggregation
                    individual_meme_data_dict = construct_meme_data_tracker_dict()
                    # Update the meme_record_id to ensure uniqueness.
                    meme_record_id += 1
                # if random.randint(0, 5000) < 5:
                    # break
        except UnicodeDecodeError:
            print(f'Unicode Decode Error. Character Mapped to undefined')
    write_to_json_file(output_json_writer, output_json_file_data)
    return meme_record_id


def convert_txt_files_from_directory(input_directory_path: str, file_extension: str, output_json_directory_path: str,
                                     file_names_list: List[str] = list()) -> None:
    """
    This function is responsible to convert the data about memes from various txt files present under the given input
    directory to data in JSON format in corresponding JSON files so that the data can be easily loaded into MongoDB
    for our storage.

    Args:
        :param input_directory_path: The path to the directory which will contain the input txt files (these txt
        files have been collected from the SNAP memetracker dataset)
        :param file_extension: The extension for the input txt files
        :param output_json_directory_path: The path to the directory where the output JSON files should be saved.
        :param file_names_list: Optional argument specifying whether only want to process particular files present in
                                the input directory. This argument is the list of the names of the files which should
                                be converted. If left empty all the files present in the input directory are converted
                                into their JSON representation.

    Returns:
        :return: None
    """
    # Check whether the given directory exist or not
    if not exist_directory(input_directory_path):
        print(f'The given directory path for the input {file_extension} files is invalid. Given {input_directory_path}')
        return None
    else:
        # Check whether the output directory exist or not.
        if not os.path.isdir(output_json_directory_path):
            try:
                # If the directory does not exist, try to construct it.
                os.makedirs(output_json_directory_path)
            except FileNotFoundError:
                # Catch the error if directory cannot be constructed
                print(f'Invalid path to the JSON files Output directory. Given {output_json_directory_path}')
                return
        # Get the file names from the given input directory with the given extension if the file_names_list argument
        # is empty. Otherwise only use the file names present in the given list
        input_file_names = file_names_list if file_names_list else get_file_names(input_directory_path, file_extension)
        # Iterate through each of these files and produce the corresponding output JSON files
        record_id = 0
        for input_file_name in input_file_names:
            # Update the record id to make sure that the id is unique across different files
            record_id = convert_txt_file_to_json(input_directory_path, input_file_name, file_extension,
                                                 output_json_directory_path, record_id)
    return None


# Main function responsible to call the convert_files function
def main():
    convert_txt_files_from_directory('../../data/sample_file', '.txt', '../../data/sample_output')


# Calling the main function
if __name__ == '__main__':
    main()
