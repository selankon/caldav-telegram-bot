# Create a template for the message that will be sent to the user. This will be used to format the message that is sent to the user.
# The template will content two variables, the event summary and the event description
#
MESSAGE_TEMPLATE = """
⏰Recordatori⏰
<b>{summary}</b>
{description}
{location}
"""

REFETCH_INTERVAL = 120  # seconds