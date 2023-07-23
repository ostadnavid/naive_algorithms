import urllib, os, re

base_error_msg = "something went wrong while {info}. Error: `{error}`"

# helper function to find extension file based on url
def find_ext(url:str):
    # image data
    if url.startswith('data:image'):
        return url[url.index('/')+1: url.index(';')]
    else:
        return 'txt'

def read_from_internet(url: str, save_path: tuple[str, str] | str='./', force_save=False, verbose=1) -> int:
    """Write contents (bytes) from url to specified path
    
    ### args
        - `url` : the url of the file you want to download.
        - `save_path` : a tuple (save_directory, file_name + .file_extension) or string 'directory/filename.extension'
            - by default the extension of file specified in `url` will be used if available, otherwise .txt will be default file extension.
            - if you don't specifie the filename(basename) file names with pattern 'file_i.ext' where i is index
        
        - `force_save` : if True rewrites(if exists) the content on the specified path(even if there is already a file on the path).
        - `verbose` : if -1 there is no print message. if 0 unnecessary prints will ignored
    ### returns
        - `-1` : an error occured and operation canceled
        - `0` : will occure if program canceled based on some condition (not an error)
            - for example if `force_save` is set to `False` and there is a file on `save_path`
        - `1` : operation was successful
        
        - if an error with type `urllib.error.HTTPError` occures. status code of the request will be returned
    ### other info
        - `duplicate content handling`: if the `save_path` is in form file_i.ext and the `force_save=False`. \
            if the content and the last file (file_i-1.ext) is same the content won't be saved 
    """
    
    # cancel operation if there a file already in path and force_save is true

    if len(save_path) == 2 and type(save_path) == tuple:
        save_path = list(save_path) 

    # check weather the file name should be `file_i.ext`. if yes figure out the filename
    if save_path[1] == '' and type(save_path) == list:
        if any([p.startswith('file_') for p in os.listdir(save_path[0])]):
            last_index = [p.split('_') for p in os.listdir(save_path[0]) if p.startswith('file_')]
            
            last_index = max([int(li[1].split('.')[0]) for li in last_index])
            
            save_path[1] = f'file_{last_index+1}'
        else:
            save_path[1] = 'file_0'
    elif os.path.basename(save_path) == '' and type(save_path) == str:
        if any([p.startswith('file_') for p in os.listdir(save_path[0])]):
            last_index = [p.split('_') for p in os.listdir(save_path[0]) if p.startswith('file_')]
            
            last_index = max([int(li[1].split('.')[0]) for li in last_index])
            
            save_path = os.path.join(save_path , f'file_{last_index+1}')
        else:
            save_path = os.path.join(save_path ,'file_0')
    else:
        if any([p.startswith('file_') for p in os.listdir(save_path[0])]):
            last_index = [p.split('_') for p in os.listdir(save_path[0]) if p.startswith('file_')]
            
            last_index = max([int(li[1].split('.')[0]) for li in last_index])
        else:
            last_index = -1
    
    save_path = ''.join(save_path) if len(save_path) == 2 else save_path
    
    # figure out extension file
    extension = 'txt'
    
    ext_pattern = r'\.(\w+)$'

    ext_match_url = re.search(ext_pattern, url, re.MULTILINE)
    
    ext_match_path = re.search(ext_pattern, save_path, re.MULTILINE)
    
    try:
        extension = ext_match_path.group(1) if ext_match_path else ext_match_url.group(1)
    except AttributeError:
        if find_ext(url) == extension:
            print(f'couldn\'t find any file extension on both specified url and path(`{save_path}`).')
        else:
            extension = find_ext(url)
    except BaseException as err:
        print(base_error_msg.format(info='finding file extension',
                                    error=err))

    save_path = save_path + '.' + extension if ext_match_path == None else save_path
    
    if os.path.exists(''.join(save_path)) and os.path.isfile(''.join(save_path)) and not force_save:
        
        if verbose != -1:
            print(f'there is a file on {save_path} . content not saved')
        return 0

    # make request
    try:
        response = urllib.request.urlopen(url)
    except urllib.error.URLError as err:
        print(base_error_msg.format(info='sending request to url',
                                    error=err))
        return -1
    except urllib.error.HTTPError as err:
        print(base_error_msg.format(info='sending request to url',
                                    error=err))
        return err.code
    except BaseException as err:
        print(base_error_msg.format(info='making request',
                                    error=err))
        return -1
    
    # read request
    try:
        content = response.read()
    except BaseException as err:
        print(base_error_msg.format(info='reading content',
                                    error=err))
        return -1

    # handle duplicate content files
    try:
        if (not force_save) and (not 'file_0' in save_path) and ('file_' in save_path)\
            and (last_index != -1):
            with open(save_path.replace(f'{last_index+1}', f'{last_index}'), 'rb') as file_2:
                content_file_2 = file_2.read()
            
            if content == content_file_2:
                if verbose != -1:
                    print(f"the content of file '{save_path.replace(f'{last_index+1}', f'{last_index}')}' matched exactly with the current request data.")
                
                return 0
    except FileNotFoundError as err:
        if not verbose <= 0:
            print(f'a minor error occured while handling duplicate content. Error: `{err}`')
    
    # save content
    try:
        with open(save_path, 'wb') as f:
            f.write(content)
        
        if not verbose <= 0:
            print(f'{"force" if force_save else ""} saved content to {save_path} successfully.')
        return 1
    except BaseException as err:
        print(base_error_msg.format(info='writing data to disk',
                                    error=err))
        return -1