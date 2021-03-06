def get_response_text(status_code):
    print("Sending response {}".format(status_code))

    if status_code == 200:
        return "Added to your mind.", "success"
    elif status_code == 404:
        return "No Notion credentials where provided. Please add them on the server.", "error"
    elif status_code == 204:
        return "Title and Url was modified correctly", "success"
    elif status_code == 205:
        return "Tags updated succesfully", "success"
    elif status_code == 429:
        return "Too much requests to Notion API", "error"
    elif status_code == 400:
        return "Invalid url provided", "error"
    else:
        return "Invalid url or text was provided.", "error"
