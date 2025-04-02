from app.db.mongodb import get_database


async def get_mistake_context_transcript(user_id: str, max_mistakes: int = 5) -> str:
    db = get_database()
    pipeline_embedded = [
        {'$match': {'user_id': user_id, 'responses.is_correct': False}},
        {'$lookup': {
            'from': 'quizzes',
            'localField': 'quiz_id',
            'foreignField': 'quiz_id',
            'as': 'quiz_info'
        }},
        {'$unwind': '$quiz_info'},
        {'$unwind': '$responses'},
        {'$match': {'responses.is_correct': False}},
        {'$sort': {'attempted_at': -1}},
        {'$limit': max_mistakes * 5},
        {'$project': {
            '_id': 0,
            'quiz_id': '$quiz_id',
            'response': '$responses',
            'questions': '$quiz_info.questions'
        }},
        {'$project': {
            'response': 1,
            'question': {
                '$filter': {
                    'input': '$questions',
                    'as': 'q',
                    'cond': {'$eq': ['$$q.question_id', '$response.question_id']}
                }
            }
        }},
        {'$unwind': '$question'}
    ]

    try:
        wrong_answers_details = await db.quiz_attempts.aggregate(pipeline_embedded).to_list()
    except Exception as e:
        raise ValueError(f"Database error fetching mistakes: {e}") from e

    if not wrong_answers_details:
        raise ValueError("No past incorrect answers found to create a practice quiz.")
    print("wrong answers details")

    # --- Format Context ---
    mistake_contexts = []
    processed_q_ids = set()
    added_count = 0
    for item in wrong_answers_details:
        if added_count >= max_mistakes:
            break

        question = item.get('question')
        response = item.get('response')
        if not question or not response or question.get('question_id') in processed_q_ids:
            continue

        question_id = question.get('question_id')
        processed_q_ids.add(question_id)

        selected_choice = next((c for c in question.get('choices', []) if c.get('choice_id') == response.get('selected_choice_id')), None)
        correct_choice = next((c for c in question.get('choices', []) if c.get('choice_id') == question.get('correct_choice_id')), None)

        if selected_choice and correct_choice and question.get('question_text') and selected_choice.get('choice_text') and correct_choice.get('choice_text'):
            mistake_contexts.append(
                f"Question: {question.get('question_text', 'N/A')}\n"
                f"User's incorrect answer: {selected_choice.get('choice_text', 'N/A')}\n"
                f"Correct answer: {correct_choice.get('choice_text', 'N/A')}\n"
                f"Explanation: {question.get('answer_explanation', 'N/A')}"
            )
            added_count += 1
        else:
            print(f"Skipping context for question {question_id} due to missing data.")

    if not mistake_contexts:
        print(f"Could not construct any valid context from DB results for user {user_id}")
        raise ValueError("Could not construct context from past mistakes (missing or inconsistent data?).")

    final_context_transcript = "\n\n---\n\n".join(mistake_contexts)
    return final_context_transcript
