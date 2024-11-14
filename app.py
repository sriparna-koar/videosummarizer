import googleapiclient.discovery
from transformers import pipeline
import streamlit as st
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from deep_translator import GoogleTranslator

# Set your API keys
YOUTUBE_API_KEY = 'AIzaSyDgOfYwjZZf8nTHWaj-At4iyWZJJaMREDM'
HUGGINGFACE_API_TOKEN = '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'

# Initialize YouTube API client
def get_youtube_client():
    return googleapiclient.discovery.build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# Fetch video details
def fetch_video_details(video_url):
    try:
        video_id = video_url.split("v=")[1]
        youtube = get_youtube_client()
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        )
        response = request.execute()
        
        if not response['items']:
            return None

        video_data = response['items'][0]
        details = {
            "video_id": video_id,
            "title": video_data["snippet"]["title"],
            "description": video_data["snippet"]["description"],
            "published_at": video_data["snippet"]["publishedAt"],
            "view_count": video_data["statistics"].get("viewCount", "N/A"),
            "like_count": video_data["statistics"].get("likeCount", "N/A"),
            "comment_count": video_data["statistics"].get("commentCount", "N/A"),
            "duration": video_data["contentDetails"]["duration"],
        }
        
        return details
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None
def fetch_and_translate_transcript(video_id):
    try:
        # First, try to get the transcript in English
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            transcript_text = " ".join([entry['text'] for entry in transcript])
            return transcript_text  # Return as is if English is available

        except:
            # Try Hindi or other common languages if English is not available
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'hi', 'bn', 'es', 'fr', 'de', 'zh', 'ar', 'ru', 'ja', 'pt', 'it', 'ko', 'nl', 'tr', 'pl', 'sv', 'cs', 'da', 'fi', 'el', 'no', 'ro', 'hu', 'sk'])  # Add more languages if needed
            transcript_text = " ".join([entry['text'] for entry in transcript])

            # Translate from detected language (Hindi/Bengali) to English
            detected_lang = transcript[0].get('language_code', 'en')
            translated_text = GoogleTranslator(source=detected_lang, target='en').translate(transcript_text)
            return translated_text

    except Exception as e:
        st.warning(f"Transcript not available in any language: {e}")
        return None

# def fetch_and_translate_transcript(video_id):
#     try:
#         try:
#             transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
#         except:
#             transcript = YouTu
# beTranscriptApi.get_transcript(video_id, languages=['bn'])
#             transcript_text = " ".join([entry['text'] for entry in transcript])
#             translated_text = GoogleTranslator(source='bn', target='en').translate(transcript_text)
#             return translated_text
#         transcript_text = " ".join([entry['text'] for entry in transcript])
#         return transcript_text
#     except Exception as e:
#         st.warning(f"Transcript not available: {e}")
#         return None
def generate_summary(text, max_length=100):
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    payload = {
        "inputs": text,
        "parameters": {"max_length": max_length, "min_length": 30, "do_sample": False},
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    summary = response.json()
    
    # Handle potential errors from the API
    if "error" in summary:
        return "Error in generating summary: " + summary["error"]
    return summary[0]["summary_text"]

# Get video summary including transcript
def get_video_summary(video_url):
    video_details = fetch_video_details(video_url)
    
    if not video_details:
        return "Video not found or invalid URL."
    
    # Fetch the transcript and summarize
    transcript_text = fetch_and_translate_transcript(video_details["video_id"])
    if transcript_text:
        summary = generate_summary(transcript_text)
    else:
        summary = "Transcript not available for this video."

    video_overview = {
        "Title": video_details["title"],
        "Published Date": video_details["published_at"],
        "Views": video_details["view_count"],
        "Likes": video_details["like_count"],
        "Comments": video_details["comment_count"],
        "Duration": video_details["duration"],
        "Description": video_details["description"],
        "Transcript Summary": summary
    }
    
    return video_overview

# Streamlit app
st.title("YouTube Video Analyzer")
video_url = st.text_input("Enter YouTube Video URL")

if st.button("Analyze Video"):
    if video_url:
        video_summary = get_video_summary(video_url)
        if isinstance(video_summary, dict):
            st.subheader("Detailed Video Overview")
            for key, value in video_summary.items():
                st.write(f"**{key}:** {value}")
        else:
            st.error(video_summary)
    else:
        st.warning("Please enter a YouTube video URL.")

# import googleapiclient.discovery
# from transformers import pipeline
# import streamlit as st
# import requests
# # Set your API keys
# YOUTUBE_API_KEY = 'AIzaSyDgOfYwjZZf8nTHWaj-At4iyWZJJaMREDM'
# HUGGINGFACE_API_TOKEN = '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'

# # Initialize YouTube API client
# def get_youtube_client():
#     return googleapiclient.discovery.build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# # Fetch video details
# def fetch_video_details(video_url):
#     try:
#         # Extract video ID from URL
#         video_id = video_url.split("v=")[1]
        
#         # Call YouTube API to get video details
#         youtube = get_youtube_client()
#         request = youtube.videos().list(
#             part="snippet,contentDetails,statistics",
#             id=video_id
#         )
#         response = request.execute()
        
#         if not response['items']:
#             return None

#         video_data = response['items'][0]
#         details = {
#             "title": video_data["snippet"]["title"],
#             "description": video_data["snippet"]["description"],
#             "published_at": video_data["snippet"]["publishedAt"],
#             "view_count": video_data["statistics"].get("viewCount", "N/A"),
#             "like_count": video_data["statistics"].get("likeCount", "N/A"),
#             "comment_count": video_data["statistics"].get("commentCount", "N/A"),
#             "duration": video_data["contentDetails"]["duration"],
#         }
        
#         return details
#     except Exception as e:
#         st.error(f"An error occurred: {e}")
#         return None
# def generate_summary(text, max_length=100):
#     headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
#     API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
#     payload = {
#         "inputs": text,
#         "parameters": {"max_length": max_length, "min_length": 30, "do_sample": False},
#     }
#     response = requests.post(API_URL, headers=headers, json=payload)
#     summary = response.json()
    
#     # Handle potential errors from the API
#     if "error" in summary:
#         return "Error in generating summary: " + summary["error"]
#     return summary[0]["summary_text"]

# def get_video_summary(video_url):
#     video_details = fetch_video_details(video_url)
    
#     if not video_details:
#         return "Video not found or invalid URL."

#     description = video_details["description"]
#     st.info("Fetching detailed summary for the video description...")
#     summary = generate_summary(description)

#     video_overview = {
#         "Title": video_details["title"],
#         "Published Date": video_details["published_at"],
#         "Views": video_details["view_count"],
#         "Likes": video_details["like_count"],
#         "Comments": video_details["comment_count"],
#         "Duration": video_details["duration"],
#         "Description Summary": summary
#     }
    
#     return video_overview

# # Streamlit app
# st.title("YouTube Video Analyzer")
# video_url = st.text_input("Enter YouTube Video URL")

# if st.button("Analyze Video"):
#     if video_url:
#         video_summary = get_video_summary(video_url)
#         if isinstance(video_summary, dict):
#             st.subheader("Detailed Video Overview")
#             for key, value in video_summary.items():
#                 st.write(f"**{key}:** {value}")
#         else:
#             st.error(video_summary)
#     else:
#         st.warning("Please enter a YouTube video URL.")
