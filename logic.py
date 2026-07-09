import requests
from urllib.parse import quote
#pip install requests
#py -m pip install requests
class imageAPI:

    def dowload_image(self,prompt, save_path="generated_image.png"):
        url = f"https://image.pollinations.ai/image/{quote(prompt)}"
        try:
            response = requests.get(url)
            with open(save_path, "wb") as f:
                f.write(response.content)
            print(f"Image saved to {save_path}")
            return True
        except Exception as e:
            print(f"Error downloading image: {e}")
            return False

if __name__ == "__main__":
    prompt = input(" void ")
    api = imageAPI()
    api.dowload_image(prompt)
