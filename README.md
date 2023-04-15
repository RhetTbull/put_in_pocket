# Put in Pocket

Simple command line tool to add URLs to Pocket.

## Synopsis

    put_in_pocket FILE_OR_URL [FILE_OR_URL ...]

## Description

Put in Pocket is a simple command line tool to add URLs to Pocket.
It takes one or more URLs or files containing a URL as arguments and adds them to your Pocket account.

If the argument is a file, the first URL found in the file is added to Pocket (subsequent URLs are ignored).
This mode of operation is primarily designed to find a URL in an email message and add it to Pocket.
See [#motivation-for-building-this-tool](Motivation for building this tool) for more details.

## Installation

`pip install --user put_in_pocket`

or

`pipx install put_in_pocket`

## Configuration

Before running `put_in_pocket` for the first time, you will need to obtain a consumer key from Pocket.
You can do this by creating an application at [https://getpocket.com/developer/apps/new](https://getpocket.com/developer/apps/new).

You will need to give your application a name and a description, and ensure that `add` permission is selected.

![The new Pocket app configuration page](https://raw.githubusercontent.com/RhetTbull/put_in_pocket/main/NewPocketApp.png "The new Pocket app configuration page")

The first time you run `put_in_pocket`, it will ask you to authorize it to access your Pocket account.

After you get your consumer key, run `put_in_pocket --authorize` and follow the instructions.

You'll need to enter your consumer key then follow the link to Pocket to authorize the application.

If you already have a Pocket access token, you can specify it on the command line with the `--authorize` and `--access-token` options:

`put_in_pocket --authorize --consumer-key 123456-7c1d9ad1324ae57564297c142 --access-token 12345-abcd-2df4-xyz-21345`

(No, those are not real keys.)

Once you have authorized `put_in_pocket`, it will store your access token in the [XDG config directory](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html) in a file named `config.toml` which for my Mac is `~/.config/put_in_pocket/config.toml`.

Unless you specify the `--no-log` option when running, `put_in_pocket` will also log to a file in the [XDG data directory](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html) in a file named `put_in_pocket.log` which for my Mac is `~/.local/share/put_in_pocket/put_in_pocket.log`.

## Motivation for building this tool

I have been a heavy Pocket user for many years and the "email to Pocket" feature is a big part of my workflow
because I often want to add URLs from devices on which I cannot install the Pocket app or browser extension.
Pocket announced in April 2023 that they were [discontinuing the email to Pocket feature](https://help.getpocket.com/article/1020-saving-to-pocket-via-email).
I was disappointed by this and decided to build a tool to replace it.

To use this tool to replace the email to Pocket feature, you will need to configure your email client to save the email message
to a file then run `put_in_pocket` on that file. I use a Mac with Apple Mail so I use the [Rules](https://support.apple.com/guide/mail/use-rules-to-manage-emails-you-receive-mlhlp1017/mac#:~:text=Use%20rules%20to%20manage%20emails%20you%20receive%20in,message.%205%20Specify%20the%20conditions.%20More%20items%20)
feature to save the message to a file then run `put_in_pocket` on that file using an AppleScript rule.

![Screenshot of Apple Mail rule](https://raw.githubusercontent.com/RhetTbull/put_in_pocket/main/Apple_Mail_rule.png "Apple Mail rule")

To trigger the rule, I have the rule run on messages sent to my email address with a "+add" appended to the email address.
This is known as [email subaddressing](https://zemalf.com/1418/email-sub-addressing/#:~:text=What%20is%20email%20sub-addressing%3F%201%20You%20can%20add,%2Btag%20qualifiers%20to%20effectively%20create%20infinite%20email%20sub-addresses.) and is supported by most email providers.
You could also use a dedicated email address for this purpose or use "add" in the subject line of the email, etc.

The `save_to_pocket` AppleScript I use to save the email and run `put_in_pocket` is available in [here](https://raw.githubusercontent.com/RhetTbull/put_in_pocket/main/save_to_pocket.applescript).

```applescript
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
```

## Command Line Tool

To see all options, run `python3 -m put_in_pocket --help`:

```
Usage: put_in_pocket.py [OPTIONS] [FILE_OR_URL]...

  Add URL or the first URL found in a text FILE to Pocket.

  FILE_OR_URL can be a URL or a path to a text file containing a URL (for
  example, an email message in .eml or .txt format)

  If FILE_OR_URL is a file and it contains multiple URLs, only the first URL
  will be added to Pocket.

  You may specify multiple FILE_OR_URL arguments.

Options:
  --version            Show the version and exit.
  --verbose            Print verbose output.
  --log / --no-log     Log to file: /Users/rhet/.local/share/put_in_pocket/put
                       _in_pocket.log.
  --dry-run            Dry run mode; don't add URL to Pocket.
  --consumer-key TEXT  Pocket API consumer key; can also be specified in
                       POCKET_CONSUMER_KEY environment variable or loaded from
                       /Users/rhet/.config/put_in_pocket/config.toml.
  --access-token TEXT  Pocket API access token; can also be specified in
                       POCKET_ACCESS_TOKEN environment variable or loaded from
                       /Users/rhet/.config/put_in_pocket/config.toml.
  --authorize          Authenticate with Pocket to get access token hen exit;
                       will store access token in
                       /Users/rhet/.config/put_in_pocket/config.toml.
  --help               Show this message and exit.
```

## License

MIT License, Copyright (c) 2023, Rhet Turnbull

## Contributing

Bug reports and pull requests are welcome on [GitHub](https://github.com/RhetTbull/put_in_pocket).
