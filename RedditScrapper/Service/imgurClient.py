from imgurpython import ImgurClient

# Replace with your Imgur API credentials
client_id = 'cb831e2d53b64cb'
client_secret = '4ed7ba8b9b60d52ac72de2ebf04b26740779685b'

# Initialize the Imgur client
client = ImgurClient(client_id, client_secret)
def uploadImage(path):
    # Path to the image file
    

    # Upload the image
    response = client.upload_from_path(path=path, config=None, anon=True)

    # Print the image link
    print(f"Image URL: {response['link']}")
    return response['link']
