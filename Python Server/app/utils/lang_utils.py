def get_response_text(status_code):
    print("Sending response {}".format(status_code))

    if status_code == 200:
        return "Added to your mind.", "success"
    elif status_code == 404:
        return "No Notion credentials where provided. Please add them on the server.", "error"
    elif status_code == 204:
        return "Title and Url was modified correctly", "success"
    else:
        return "Invalid url or text was provided.", "error"
