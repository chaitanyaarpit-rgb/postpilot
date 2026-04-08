import json


def generate_post_content(topic: dict, ctx: dict, openai) -> dict:
    """Generate caption + hashtags for a post."""
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"You are a LinkedIn content writer. {ctx['context_prompt']}"},
            {"role": "user", "content": f"""Write a LinkedIn post.

Topic: {topic['topic']}
Angle: {topic['angle']}
Content Type: {topic.get('content_type', 'post')}

Requirements:
- Hook in first line
- 150-250 words
- 3-5 hashtags
- CTA at end
- Tone: {ctx['tone']}

Return JSON: caption, hashtags (array), image_prompt (DALL-E prompt)
"""},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)
