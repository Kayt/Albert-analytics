"""
Suppose you have some texts of news and know their categories.
You want to train a system with this pre-categorized/pre-classified 
texts. So, you have better call this data your training set.
"""
# import nltk

from dataset import newsSet
# from bank.bank import newsSet
from naiveBayesClassifier.classifier import Classifier
from naiveBayesClassifier.tokenizer import Tokenizer
from naiveBayesClassifier.trainer import Trainer


token = Tokenizer()

newsTrainer = Trainer()


# You need to train the system passing each text one by one to the trainer module.
# newsSet = [
#     {'question': 'Is there a 24 hour Customer Contact Centre?',
#         'answer': 'Yes, we have a 24 Hour Customer Contact Centre where you can get support related to your banking enquiries. You can call the numbers: +263 772 244 788, +263...'},
#     {'question': 'Is there a 24 hour Customer Contact Centre?',
#         'answer': 'Yes, we have a 24 Hour Customer Contact Centre where you can get support related to your banking enquiries. You can call the numbers: +263 772 244 788, +263...'},
#     {'question': 'Is there a way I can check my account balance other than contacting the branch?',
#         'answer': 'Yes, you can check your balance through our ATM network, NMBMobile App or Internet Banking.'},
#     {'question': 'What is an e-Statement?',
#         'answer': 'An e-Statement is an electronic version of your paper bank statement which is emailed directly to your registered email address in a password protected PDF ...'},
#     {'question': 'How can I transfer money to a bank account abroad?',
#         'answer': 'This service is currently available for Corporate clients only, subject to availability of funds and the RBZ priority payments list'},
#     {'question': 'How do I get internal funds transfer forms?',
#         'answer': 'We are no longer accepting paper transfer forms, please register for Mobile Banking at your nearest branch or enrol for Internet Banking here.'},
#     {'question': 'How can I get a Point of Sale Machine for my business?',
#         'answer': 'You can submit an application letter detailing the following : Business name Bank account number Nature of business Contact person & number Number...'}
# ]
for news in newsSet:
    newsTrainer.train(news['question'], news['answer'])

# When you have sufficient trained data, you are almost done and can start to use
# a classifier.
newsClassifier = Classifier(newsTrainer.data, token)

# print(newsClassifier.accuracy(newsSet))

# Now you have a classifier which can give a try to classifiy text of news whose
# category is unknown, yet.
classification = newsClassifier.classify("fuck")


# the classification variable holds the detected categories sorted
for cl in classification[:5]:
    print(cl)
