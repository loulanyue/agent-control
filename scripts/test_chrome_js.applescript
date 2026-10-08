tell application "Google Chrome"
    repeat with w in windows
        repeat with t in tabs of w
            if URL of t contains "x.com/trq212" then
                set res to execute t javascript "document.querySelectorAll(\"article[data-testid='tweet']\").length"
                return "Tweet count in DOM: " & res
            end if
        end repeat
    end repeat
    return "Not found"
end tell
