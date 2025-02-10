# pixoo64-spotify-docker
Displays album art of currently playing songs from Spotify on Pixoo 64 screen with a clock in the lower right corner

Setup:
- Create a `.env` file in the root directory of the project
- Add your Pixoo 64's IP address, Spotify client ID, and Spotify client URI to the `.env` file as shown below:
  ```
  PIXOO64_IP_ADDRESS=your_pixoo64_ip_address
  SPOTIFY_CLIENT_ID=your_spotify_client_id
  SPOTIFY_CLIENT_URI=your_spotify_client_uri
  SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
  ```

Docker Setup:
- Ensure you have Docker installed on your machine
- Build the Docker image:
  ```bash
  docker build -t pixoo64-spotify-docker .
  ```
- Run the Docker container:
  ```bash
  docker run --env-file .env -d pixoo64-spotify-docker
  ```

Additional Things to Note:
- If playback of a song is stopped, the program will stop showing the image and display the default channel
- This program can't currently display art from podcast episodes, a placeholder image will be shown

Credits:
- This project is a modification of the original project by [ksassani99](https://github.com/ksassani99/pixoo64-spotify-integration)
- This project utilizes the Spotipy Python library and the SomethingWithComputers Pixoo Python library
- Spotipy library: https://github.com/plamere/spotipy
- Pixoo library: https://github.com/SomethingWithComputers/pixoo
