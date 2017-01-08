import urllib2
import json

API_BASE="https://coparkfinder-api.herokuapp.com/api/v1"

def lambda_handler(event, context):
    if (event["session"]["application"]["applicationId"] !=
        "amzn1.ask.skill.15c8f008-3cf7-4fdd-b56f-720933ad9e56"):
        raise ValueError("Invalid Application ID")

    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

def on_session_started(session_started_request, session):
    print "Starting new session."

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    if intent_name == "ParkInformation":
        return get_park_description(intent)
    elif intent_name == "ParkActivities":
        return get_park_activities(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print "Ending session."

def handle_session_end_request():
    card_title = "COParkFinder - Thanks"
    speech_output = "Thank you for using the COParkFinder skill. See you next time!"
    should_end_session = True

def get_welcome_response():
    session_attributes = {}
    card_title = "COParkFinder"
    speech_output = "Welcome to the Alexa Colorado Park Finder skill. " \
                    "You can ask me about the 42 state parks in Colorado, or " \
                    "ask me to find parks where you can do specific activities."
    reprompt_text = "Please ask me about a park or an activity, " \
                    "for example Crawford or boating."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_park_activities(intent):
    session_attributes = {}
    card_title = "Park Activities"
    speech_output = "I'm not sure which park you wanted to hear about." \
                    "Please try again."
    reprompt_text = "I'm not sure which park you wanted to hear about." \
                    "Try asking about Crawford or Rifle Falls for example."
    should_end_session = False

    if "Park" in intent["slots"]:
        intent_name = intent["slots"]["Park"]["value"]
        park_name = intent_name.title()
        query_name = park_name.replace(" ", "%20")

        card_title = "Park Activities For " + park_name

        response = urllib2.urlopen(API_BASE + "/park?name=" + query_name )
        park_info = json.load(response)

        speech_output = "Great. Let me tell you about activities at " + park_name + "!"
        speech_output += "You can do: "
        activities = park_info["activities"]
        for idx, activity in enumerate(activities):
            if idx == (len(activities) - 2):
                speech_output += activity["type"] + ", and "
            elif idx == (len(activities) -1):
                speech_output += activity["type"] + "."
            else:
                speech_output += activity["type"] + ", "

        reprompt_text = ""

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))





def get_park_description(intent):
    session_attributes = {}
    card_title = "Park Information"
    speech_output = "I'm not sure which park you wanted to hear about." \
                    "Please try again."
    reprompt_text = "I'm not sure which park you wanted to hear about." \
                    "Try asking about Crawford or Rifle Falls for example."
    should_end_session = False

    if "Park" in intent["slots"]:
        intent_name = intent["slots"]["Park"]["value"]
        park_name = intent_name.title()
        query_name = park_name.replace(" ", "%20")

        card_title = "Park Information For " + park_name

        response = urllib2.urlopen(API_BASE + "/park?name=" + query_name )
        park_info = json.load(response)

        speech_output = "Great. Let me tell you about " + park_name + "!"
        speech_output += park_info["description"]

        reprompt_text = ""

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }
