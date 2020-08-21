from notion.client import NotionClient


client = NotionClient(token_v2="5574622b5cd318cf4107d1e088041e1c2482be80a5889c12fa8264641836e14d785d528a0cea0a82b9904251019795029dfa4e6fab65d518d7d905f9854ba2fdbed19c2df98f5d68cf918a8d9afd")

# Access a database using the URL of the database page or the inline block
cv = client.get_collection_view("https://www.notion.so/glassear/d4e43dbfe7244e0a83f18e14506e74ae?v=2b6755006a15418c978d5067180baae0")

# List all the records with "Bob" in them
for row in cv.collection.get_rows(search="Bob"):
    if len(row.tags) > 0:
        print("We estimate the value of '{}' at {}".format(row.name, row.tags))

# Add a new record
row = cv.collection.add_row()
row.name = "Just some data"
row.files = ["https://www.birdlife.org/sites/default/files/styles/1600/public/slide.jpg"]
row.person = client.current_user
if "options" not in prop_schema: prop_schema["options"] = []
row.AITags = ["3D"]