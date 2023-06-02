from flask import Flask, render_template, request, redirect, url_for
import PyPDF2
import openai

openai.api_key = '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'

app = Flask(__name__)

file_uploaded = False
text = ""
conversation_history = []

@app.route('/', methods=['GET', 'POST'])
def upload():
    global file_uploaded
    global text

    if request.method == 'POST':
        file = request.files['file']
        if file:
            # Save the uploaded file to the current directory
            file.save(file.filename)

            # Extract text from the PDF file
            text = extract_text_from_pdf(file.filename)
            file_uploaded = True

    return render_template('upload.html', file_uploaded=file_uploaded, conversation=conversation_history)

def extract_text_from_pdf(filename):
    with open(filename, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

@app.route('/ask', methods=['POST'])
def ask_question():
    global conversation_history

    if request.method == 'POST':
        question = request.form['question']

        # Get a response from ChatGPT
        response = chat_with_gpt(text, question)

        # Append the user's question and AI response to the conversation history
        conversation_history.append({'user': question, 'ai': response})

    return redirect(url_for('upload'))

@app.route('/back', methods=['POST'])
def go_back():
    global file_uploaded
    global conversation_history
    file_uploaded = False
    conversation_history = []
    return redirect(url_for('upload'))

def chat_with_gpt(text, question):
    global conversation_history

    # Prepare the prompt with conversation history
    prompt = ""
    for item in conversation_history:
        prompt += f"User: {item['user']}\nAI: {item['ai']}\n"

    # Send the prompt and the user's current question to ChatGPT for a response
    prompt += f"User: {question}\nAI:"

    # Send the prompt to ChatGPT for a response
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.7
    )

    # Extract the AI response from the API response
    answer = response.choices[0].text.strip()

    # Update the conversation history
    conversation_history.append({'user': question, 'ai': answer})

    return answer

########################################################################
if __name__ == '__main__':
    app.run(debug=True)
