import torch
import torch.nn as nn
from flask import Flask, request, render_template

# Import necessary libraries
from transformers import AutoModel, BertTokenizerFast

# Define the Model Architecture
class BERT_Arch(nn.Module):
    def __init__(self, bert):
      super(BERT_Arch, self).__init__()
      self.bert = bert
      self.dropout = nn.Dropout(0.1)
      self.relu =  nn.ReLU()
      self.fc1 = nn.Linear(768, 512)
      self.fc2 = nn.Linear(512, 2)
      self.softmax = nn.LogSoftmax(dim=1)
      
    def forward(self, sent_id, mask):
      cls_hs = self.bert(sent_id, attention_mask=mask)['pooler_output']
      x = self.fc1(cls_hs)
      x = self.relu(x)
      x = self.dropout(x)
      x = self.fc2(x)
      x = self.softmax(x)
      return x

# Initialize Flask App and Load Assets
app = Flask(__name__)

# Load the tokenizer
tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')

try:
    # Instantiate the base BERT model
    bert = AutoModel.from_pretrained('bert-base-uncased')
    model = BERT_Arch(bert)
    state_dict = torch.load('c2_new_model_weights.pt', map_location=torch.device('cpu'), weights_only=True)
    model.load_state_dict(state_dict, strict=False)
    
    # Set the model to evaluation mode
    model.eval()
except FileNotFoundError:
    print("Error: Model weights file not found.")
    exit()

# Routes and App Run

@app.route('/')
def home():
    """Renders the home page."""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handles the prediction request."""
    if request.method == 'POST':
        news_text = request.form['news_text']
        if not news_text.strip():
            return render_template('index.html', prediction_text="Please enter some news text.", prediction_class="text-warning")

        MAX_LENGHT = 15
        tokens = tokenizer.batch_encode_plus(
            [news_text], max_length=MAX_LENGHT, padding='max_length', truncation=True, return_token_type_ids=False
        )
        input_ids = torch.tensor(tokens['input_ids'])
        attention_mask = torch.tensor(tokens['attention_mask'])

        with torch.no_grad():
            outputs = model(input_ids, attention_mask)
        prediction = torch.argmax(outputs, dim=1).item()

        if prediction == 1:
            result = "This news is likely FAKE."
            prediction_class = "fake-news"
        else:
            result = "This news is likely REAL."
            prediction_class = "real-news"

        return render_template('index.html',
                               prediction_text=result,
                               prediction_class=prediction_class,
                               news_text=news_text)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)