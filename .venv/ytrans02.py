from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter, TextFormatter
import textwrap

ytt_api = YouTubeTranscriptApi()

# retrieve the available transcripts
transcript_list = ytt_api.list('eG6N6W56vK0')
#transcript_list = ytt_api.list('ZfwA1u9Oxl4')
# you can directly filter for the language you are looking for
transcript = transcript_list.find_transcript(['de', 'en'])

# fetch the actual transcript data
transcript_data = transcript.fetch()

# create JSON formatter
json_formatter = JSONFormatter()
json_formatted = json_formatter.format_transcript(transcript_data)

# write JSON to file
with open('your_filename.json', 'w', encoding='utf-8') as json_file:
    json_file.write(json_formatted)

print("Transkript wurde erfolgreich in 'your_filename.json' gespeichert!")
print("\n" + "="*150 + "\n")

# create readable text output
text_formatter = TextFormatter()
text_output = text_formatter.format_transcript(transcript_data)

# wrap text to max 150 characters per line
wrapped_text = textwrap.fill(text_output, width=150)

# print to console
print("TRANSKRIPT (lesbar formatiert):\n")
print(wrapped_text)

# optionally save to text file
with open('your_filename.txt', 'w', encoding='utf-8') as text_file:
    text_file.write(wrapped_text)

print("\n" + "="*150)
print("\nText wurde auch in 'your_filename.txt' gespeichert!")
