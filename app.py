from flask import Flask

app = Flask(__name__)
#Creates Flask App Instance

@app.get("/health")#Defines GET route at /health
def health(): #Provides a simple "health check" endpoint to confirm server is running
  return {"ok": True}

@app.get("/")
def home():
  return "ivevents is running."

if __name__ == "__main__": #This is only for testing using "python app.py" command directly
  app.run(debug = True)