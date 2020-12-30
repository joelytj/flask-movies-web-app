from flask import Flask, render_template, redirect, url_for, request
import requests

app = Flask(__name__) 

app.config["DEBUG"] = True

@app.route("/")
def render_landing_page():
    return render_template("landing-page.html") 
        # render_template by default goes into template folder
    # except:
    #     return render_template("error404.html")

@app.route('/search', methods=['POST'])
def form_submit():
    user_query = request.form['search_query'] #matches name attribute of query string input (HTML)
    redirect_url = url_for('.search_imdb', query_string=user_query) #match search_imdb function name (Python flask)
    return redirect(redirect_url)

#dynamic routing in URL so that when u change url it goes to the page

@app.route("/search/<query_string>", methods=['GET']) #since landing_page form method is by POST
def search_imdb(query_string):

    url = "https://imdb8.p.rapidapi.com/title/auto-complete"

    querystring = {"q": query_string} 

    headers = {
        'x-rapidapi-key': "17860e939amshd3a115b74861472p1d10fcjsn685aaef504c2",
        'x-rapidapi-host': "imdb8.p.rapidapi.com"
    }


    try:
        response = requests.request("GET", url, headers=headers, params=querystring)
        data = response.json()
        return render_template("search-result.html", data = data)

    except:
        return render_template('error404.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")

