from agent.langgraph_agent import run_formula_update_agent
from agent.request_service import create_ai_request
from agent.schemas import AIRequestCreate


def terminal_chat():
    user_email = "abc"
    user_name = "abc"

    conversation_messages = []
    current_structured_data = {}
    latest_agent_response = None

    print("AI Formula Update Agent")
    print("Type 'exit' to quit.")
    print("Type 'submit' when the agent says the request is ready.")
    print("-" * 50)

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            break

        if user_input.lower() == "submit":
            if not latest_agent_response or not latest_agent_response.get("ready_to_submit"):
                print("Agent: Request is not ready yet.")
                continue

            data = latest_agent_response["structured_data"]

            request = AIRequestCreate(
                request_type="formula_update",
                requested_by=user_email,
                requested_by_name=user_name,

                project_id=data.get("project_id"),
                project_name=data.get("project_name"),

                category=data.get("category"),

                shape_id=data.get("shape_id"),
                shape_name=data.get("shape_name"),

                output_name=data.get("output_name"),
                current_formula=data.get("current_formula"),
                requested_formula=data.get("requested_formula"),

                reason=data.get("reason"),
                ai_summary=(
                    f"User requested formula update for "
                    f"{data.get('shape_name')} - {data.get('output_name')}."
                ),
                ai_suggestion="Admin should verify the requested formula before applying it.",
                status="pending"
            )

            request_id = create_ai_request(request)

            print("Agent: Request submitted to admin.")
            print("Request ID:", request_id)

            conversation_messages = []
            current_structured_data = {}
            latest_agent_response = None
            continue

        conversation_messages.append({
            "role": "user",
            "content": user_input
        })

        try:
            latest_agent_response = run_formula_update_agent(
                user_email=user_email,
                conversation_messages=conversation_messages,
                current_structured_data=current_structured_data
            )

            current_structured_data = latest_agent_response.get("structured_data", {})

            print("Agent:", latest_agent_response["response_to_user"])

        except Exception as e:
            print("Agent Error:", str(e))


if __name__ == "__main__":
    terminal_chat()