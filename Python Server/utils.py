import requests
import datetime

from requests import urllib3
from urllib.parse import urlsplit, urlunsplit
from bs4 import BeautifulSoup
import validators
# Request timeout
_TIMEOUT = 5
# Verbose
_VERBOSE = True
# Not only onion domains flag
_NOT_ONLY_ONION = True
# Disable insecure warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def msg(msg: str, ico: str):
    """ Shows info according to Verbosity """
    if _VERBOSE:
        print(msg)
    else:
        print(ico, end='', flush=True)


def crawl(url):
    headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    """ Web Crawling for a given URL """
    candidate_url = " "
    try:
        print(url)
        is_well_formed=validators.url(url)
        if is_well_formed:
            r = requests.get(url,headers, verify=False, timeout=_TIMEOUT)
            if r.status_code == 200:
                try:
                    soup = BeautifulSoup(r.text, "html.parser")
                    title_tag = soup.head.find("title")
                    if title_tag is None:
                        title = ""
                    else:
                        title = title_tag.contents[0]
                        title = title.replace("'", "''")  # TODO Change quotes parsing

                    description_tag = soup.head.find(name='meta', attrs={'name': 'description'})
                    if description_tag is None:
                        description = ""
                    else:
                        description = description_tag.get('content')
                        description = description.replace("'", "''")  # TODO change quotes parsing

                    last_date = datetime.datetime.now().now().strftime("%Y-%m-%d")

                    soup_image = BeautifulSoup(r.text, 'lxml')  # choose lxml parser
                    # find the tag : <img ... >
                    image_tags = soup_image.findAll('img')

                    # for i in image_tags:
                    #     print(i.get('src'))
                    #     print(i.get('title'))

                    candidate_url = [url, title, description, last_date, image_tags]
                
                except TimeoutError:
                    msg("ERROR: " + " is not responding\n     : {0}\n - - - - - - - - - - - - - - - - - - - - - - ".format(href), 'x')

                except Exception as General_Error:
                    msg("ERROR: URL generated a general error...\n     : {0}\n     : {1}\n - - - - - - - - - - - - - - - - - - - - - - ".format(href, str(General_Error)), 'x')
            else:
                msg("ERROR: Code was not 200",'x')
        else:
            msg("ERROR: not a valid URL\n     : {0}\n - - - - - - - - - - - - - - - - - - - - - - ".format(href), 'x')                        
    except TimeoutError:
        msg("ERROR: " + " is not responding\n     : {0}\n - - - - - - - - - - - - - - - - - - - - - - ".format(url),
            'x')

    except KeyboardInterrupt:
        print("\n(Ctrl + C) Terminated by user...\n")
        raise SystemExit

    except Exception as General_Error:
        msg(
            "ERROR: URL generated a general error...\n     : {0}\n     : {1}\n - - - - - - - - - - - - - - - - - - - - - - ".format(
                url, str(General_Error)), 'x')

    return candidate_url


# def crawl(url):
#     """ Web Crawling for a given URL array """
#     candidate_url = " "
#     try:
#         r = requests.get(url, verify=False, timeout=_TIMEOUT)
#         print(url)
#         if r.status_code == 200:
#             soup = BeautifulSoup(r.text, "html.parser")

#             # #for link in soup.find_all("a"):
#             # #href = soup.get("href")

#             # if href.startswith('/'):
#             #     if url.endswith('/'):
#             #         href = url[:-1] + href
#             #     else:
#             #         href = url + href

#             # # URL form checking
#             # split_href = urlsplit(href)                    
#             # well_formed = False
#             # if "http" not in split_href.scheme:
#             #     well_formed = False
#             # elif not _NOT_ONLY_ONION and not split_href.netloc.endswith(".onion"):                        
#             #     well_formed = False
#             # else:
#             #     well_formed = True
#             well_formed = True
#             # Test reachable
#             if well_formed == True:
#                 try:
#                     r_test = requests.get(href, verify=False, timeout=_TIMEOUT)

#                     if r_test.status_code == 200:
#                         msg("Found URL: Well formed and reachable\n         : {0}\n - - - - - - - - - - - - - - - - - - - - - -".format(href), 'o')

#                         soup_test = BeautifulSoup(r_test.text, "html.parser")                                

#                         title_tag = soup_test.head.find("title")          
#                         if title_tag is None:
#                             title = ""
#                         else:
#                             title = title_tag.contents[0]
#                             title = title.replace("'","''") # TODO Change quotes parsing

#                         description_tag = soup_test.head.find(name='meta', attrs={'name':'description'})
#                         if description_tag is None:
#                             description = ""
#                         else:
#                             description = description_tag.get('content')
#                             description = description.replace("'","''") # TODO change quotes parsing

#                         last_date = datetime.datetime.now().now().strftime("%Y-%m-%d")

#                         candidate_url = [href, title, description, last_date]                               


#                 except TimeoutError:
#                     msg("ERROR: " + " is not responding\n     : {0}\n - - - - - - - - - - - - - - - - - - - - - - ".format(href), 'x')

#                 except Exception as General_Error:
#                     msg("ERROR: URL generated a general error...\n     : {0}\n     : {1}\n - - - - - - - - - - - - - - - - - - - - - - ".format(href, str(General_Error)), 'x')

#             else:
#                 msg("ERROR: not a valid URL\n     : {0}\n - - - - - - - - - - - - - - - - - - - - - - ".format(href), 'x')                        

#     except TimeoutError:
#         msg("ERROR: " + " is not responding\n     : {0}\n - - - - - - - - - - - - - - - - - - - - - - ".format(url), 'x')

#     except KeyboardInterrupt:
#         print("\n(Ctrl + C) Terminated by user...\n")
#         raise SystemExit

#     except Exception as General_Error:
#         msg("ERROR: URL generated a general error...\n     : {0}\n     : {1}\n - - - - - - - - - - - - - - - - - - - - - - ".format(url, str(General_Error)), 'x')            

#     return candidate_url
def fix_list(list_to_fix):
    # check_list = isinstance(an_object, list)

    # for photo in list_to_fix:
    #     if photo.startswith(" ") and photo.endswith(" "):
    #         list_to_fix.remove(photo)
    return list_to_fix
