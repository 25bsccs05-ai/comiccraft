def build_comic_layout(
    outline,
    story,
    image_paths
):
    story_map = {
        item["panel_number"]: item
        for item in story
    }

    layout = []

    for index, panel in enumerate(outline):
        number = panel["panel_number"]

        story_item = story_map.get(
            number,
            {}
        )

        layout.append({
            "panel_number": number,
            "title": panel["title"],
            "scene_description": panel["scene_description"],
            "image_prompt": panel["image_prompt"],
            "narration": story_item.get(
                "narration",
                ""
            ),
            "dialogue": story_item.get(
                "dialogue",
                []
            ),
            "image_path": image_paths[index]
        })

    return layout