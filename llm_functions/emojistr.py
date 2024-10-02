import emoji

definition = {
        "name": "emojistr",
        "description": "Returns an emoji from a shortcode",
        "parameters": {
        "type": "object",
        "properties": {
        "emoji_shortcode": {
            "type": "string",
            "description": "The short code name of the emojis"
        }
        },
        "required": ["emoji_shortcode"]
    }
}

def emojistr(emoji_shortcode):
    emoji_str = emoji.emojize(emoji_shortcode)
    return emoji_str