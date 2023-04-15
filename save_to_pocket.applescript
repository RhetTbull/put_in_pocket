-- Runs the put_in_pocket.py script to save URL found in message body to Pocket 
-- This script should be saved to ~/Library/Application\ Scripts/com.apple.mail/
-- Then use Mail > Settings > Rules > Add Rule to create a rule to run this script when mail arrives matching your criteria
-- I use "To contains myemail+add@me.com" as the rule as you can add anything after a "+" to an email address and the email
-- will still be delivered
-- You will need to set the variable theScripPath to the path to the script you want to run (which runs put_in_pocket.py) 
-- and this must be done in the 'using terms from application "Mail"' block or the script won't be able to access the variable
-- The first URL in the subject line or body of the email will parsed and added to Pocket by put_in_pocket.py
-- however, if the content of the email is MIME formatted, URLs will not be extracted

using terms from application "Mail"
	on perform mail action with messages theMessages
		set theScriptPath to "/Users/rhet/.local/bin/put_in_pocket.sh"
		repeat with theMessage in theMessages
			set theSubject to ""
			set theBody to ""
			set theSubject to subject of theMessage
			set theBody to source of theMessage
			set uniqueID to (do shell script "uuidgen") -- generate a unique ID using the "uuidgen" command
			set theTempFile to POSIX path of (path to temporary items folder) & "save_to_pocket_" & uniqueID & ".txt"
			set theFileID to open for access theTempFile with write permission
			write theSubject & " " & theBody to theFileID
			close access theFileID
			set theCommand to theScriptPath & " " & theTempFile
			do shell script theCommand
		end repeat
	end perform mail action with messages
end using terms from