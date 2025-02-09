
            mbti_type, recommended_subjects = analyze_face(filepath)
            mbti_type = face_MBTI[mbti_type]
            recommended_subjects = [{"name": item["name"], "url": item["url"]} for item in subjects]
            return render_template('result.html', mbti_type=mbti_type, subjects=recommended_subjects, image_path=filepath)

    return render_template('upload.html')