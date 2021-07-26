tell application "Messages"
    set targetBuddy to "**phone_number**"
    set targetService to id of 1st service whose service type = iMessage
    set textMessage to "**message**"
    set theBuddy to buddy targetBuddy of service id targetService
    send textMessage to theBuddy
end tell
