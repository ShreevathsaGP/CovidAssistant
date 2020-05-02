from flask import Flask, render_template
from flask_ask import Ask, statement, question, session
from scrape import Scraper as StatisticsScraper # Scraper class from scrape.py file --> does all the statistics work!
from news import Scraper as NewsScraper # Scraper cass from news.py file --> does all the news work!
import pycountry
import country_converter as coco
from datetime import datetime, timedelta, date
import random
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = "this_is_just_here_for_fun"

@app.route('/')
def home():
    try:
        requests.get('https://www.worldometers.info/coronavirus/')
        message = "This script works when mac is asleep"
    except:
        message = 'This script fails when mac is asleep'
    return "<h1 align='center' > Hello there, this is the home page for the Alexa Sill --> Covid-19 Hub </h1> <br><br><br><br> <h2 id='date-clause' align='center'></h2><h2 align='center'><em>All rights reserved. <strong>Made by Shreevathsa GP</strong></em></h2><br><br><br><br><br><h5 align='center'>{}</h5><script>year = '&copy;' + new Date().getFullYear(); console.log(year); document.getElementById('date-clause').innerHTML = year</script>".format(message)

ask = Ask(app, '/covid-19')

@ask.launch
def launch():
    print("\nLaunched at --> {}\n".format(datetime.now()))
    testing_message = "Hello there, welcome to the alexa covid-19 hub!"
    return statement("Hello there, welcome to the alexa covid-19 hub! To ask the latest global statistics, say: alexa, ask the covid kid for global stats. Or for stats from a specific country, say: alexa, ask the covid kid for stats from (and then the specific country's name). Furthermore, for the latest global covid-19 news, say: alexa, ask the covid kid for global news. Or for updates in a specific country say: alexa, ask the covid kid for latest news in (and then the specific country's name). Go ahead, try it out, say alexa ask the covid kid: (and then any of the commands i mentioned!).")

@ask.intent("test")
def test():
    print("\nTest conducted at --> {}\n".format(datetime.now()))
    testing_message = "Hello there, welcome to the alexa covid-19 hub!"
    return statement("{}".format(testing_message))


""" STATISTICS """
@ask.intent("global_stats")
def global_stats():
    print("\nRequested global statistics at --> {}\n".format(datetime.now()))
    
    data = StatisticsScraper().global_stats()

    try:
        data = StatisticsScraper().global_stats()
    except:
        print("    Problem getting global statistics at --> {}\n".format(str(datetime.now())))
        return statement("The global statistics are not available at the moment!")

    global_total = data['total_cases']
    global_deaths = data['total_deaths']
    global_recoveries = data['total_recoveries']
    global_active = data['active_cases']

    return statement("Currently in the world, there are {} active cases, {} total deaths, {} total recoveries and a total of {} cases recorded overall.".format(global_active, global_deaths, global_recoveries, global_total))

@ask.intent("country_stats")
# The parameter country_name is automatically configured in ammazon developer Alexa Skills kit
def country_stats(country_name):
    print("\nRequested {} country statistics at --> {}\n".format(str(country_name), datetime.now()))
    if country_name.lower() in ['uk', 'england', 'scotland', 'wales', 'northern ireland']:
        country_name = "United Kingdom"
    else:
        pass

    country_name_list = coco.convert(names=[country_name], to='ISO2', not_found=None)
    print("    The ISO for country is -> {}\n".format(country_name_list))
    search_country = country_name_list
    try:
        data = StatisticsScraper().country_stats(search_country)
    except:
        print("    Problem getting {} country statistics at --> {}\n".format(str(country_name), str(datetime.now())))
        return statement("If you are using an abbreviation for your country, please use the full form instead, if not, i am very sorry! But I was not able to get the covid-19 statistics for {}!".format(country_name))
    
    # Formatting in scraper.py: return {'country_cases':country_total_cases, 'country_deaths':country_total_deaths, 'country_recoveries':country_total_recoveries, 'country_active':country_active_cases}
    if data == 'CountryError':
        return statement("If you are using an abbreviation for your country, please use the full form instead, if not, i am very sorry! But the statistics for {} are currently unavailable".format(country_name))
    else:
        country_total = data['country_cases']
        country_deaths = data['country_deaths']
        country_recoveries = data['country_recoveries']
        country_active = data['country_active']

        if country_total == "ScrapeError":
            return statement("I am very sorry! But the statistics for {} are currently unavailable".format(country_name))
        else:
            pass

        if country_deaths == "ScrapeError":
            country_deaths = "an unknown number of"
        else:
            pass
        
        if country_recoveries == "ScrapeError":
            country_recoveries = "an unknown number of"
        else:
            pass

        return statement("In {}, currently, there are {} active cases, {} total deaths, {} total recoveries and a total of {} cases recorded overall.".format(country_name, country_active, country_deaths, country_recoveries, country_total))

""" STATISTICS """


""" NEWS """
@ask.intent("global_news")
def global_news():
    print("\nRequested global news at --> {}\n".format(datetime.now()))
    
    global_news = NewsScraper().get_global_news()
    try:
        global_news = NewsScraper().get_global_news()
    except:
        print("    Problem getting global news at --> {}\n".format(str(datetime.now())))
        return statement("The global news are not available at the moment!")
    
    global_statement = ''
    
    """ RANDOM FILLERS """
    continuity_statements = ['Moving on, ', 'Furthermore, ', 'Next up, ', 'In other news, ', 'Next in line, ']
    author_statements = ['As reported by ', 'Reports from ', 'Sourced from ', 'Written by ', 'Coming in fresh from ', 'Coming from ']

    """ RANDOM FILLERS """
    
    reference_list = list(global_news.values())

    for author, description in global_news.items():
        if description == reference_list[-1]:
            if author == 'None' or author == '' or author == None or author == ' None' or author == 'Unknown' or author == 'None ':
                global_statement += " {} {}: {} . ".format(str(random.choice(author_statements)), str("an unknown reporter"), str(description))
            else:
                global_statement += " {} {}: {} . ".format(str(random.choice(author_statements)), str(author), str(description))
        else:
            if author == 'None' or author == '' or author == None or author == ' None' or author == 'Unknown' or author == 'None ':
                global_statement += " {} {}: {} . ".format(str(random.choice(author_statements)), str("an unknown reporter"), str(description))
            else:
                global_statement += " {} {}: {} .  {}".format(str(random.choice(author_statements)), str(author), str(description), str(random.choice(continuity_statements)))
    
    return statement("{}".format(global_statement))

@ask.intent("country_news")
# The parameter country_name is automatically configured in ammazon developer Alexa Skills kit
def country_news(country_name):
    print("\nRequested {} country news at --> {}\n".format(str(country_name), datetime.now()))
    if country_name.lower() in ['uk', 'england', 'scotland', 'wales', 'northern ireland']:
        country_name = "United Kingdom"
    else:
        pass

    country_name_list = coco.convert(names=[country_name], to='ISO2', not_found=None)
    print("    The ISO for country is -> {}\n".format(country_name_list))
    search_country = country_name_list.lower()

    try:
        country_news = NewsScraper().get_country_news(search_country)
    except:
        print("    Problem getting {} country news at --> {}\n".format(str(country_name), str(datetime.now())))
        return statement("If you are using an abbreviation for your country, please use the full form instead, if not, i am very sorry! But I was not able to get any news on covid-19 in {}!".format(country_name))

    country_statement = 'The latest news from {}: '.format(country_name)

    """ RANDOM FILLERS """
    continuity_statements = ['Moving on, ', 'Furthermore, ', 'Next up, ', 'In other news, ', 'Next in line, ']
    author_statements = ['As reported by ', 'Reports from ', 'Sourced from ', 'Written by ', 'Coming in fresh from ', 'Coming from ']
    # These are here to make the alexa speech more conversational.
    """ RANDOM FILLERS """
    
    reference_list = list(country_news.values())

    for author, description in country_news.items():
        if description == reference_list[-1]:
            if author == 'None' or author == '' or author == None or author == ' None' or author == 'Unknown' or author == 'None ':
                country_statement += " {} {}: {} . ".format(str(random.choice(author_statements)), str("an unknown reporter"), str(description))
            else:
                country_statement += " {} {}: {} . ".format(str(random.choice(author_statements)), str(author), str(description))
        else:
            if author == 'None' or author == '' or author == None or author == ' None' or author == 'Unknown' or author == 'None ':
                country_statement += " {} {}: {} . ".format(str(random.choice(author_statements)), str("an unknown reporter"), str(description))
            else:
                country_statement += " {} {}: {} . {}".format(str(random.choice(author_statements)), str(author), str(description), str(random.choice(continuity_statements)))

    return statement("{}".format(country_statement))

""" NEWS """

""" BUILTINS """
@ask.intent("AMAZON.FallbackIntent")
# This intent is if what the user askd does not match the utterance of any other custom intents
def fallback():
    print("Fallback intent at --> {}".format(datetime.now()))
    return statement("I did not quite understand, please repeat!")

@ask.intent("AMAZON.CancelIntent")
# This intent is if the user cancels
def cancel():
    print("Cancel intent at --> {}".format(datetime.now()))
    return statement("It was great talking to you, hope to do it again!")

@ask.intent("AMAZON.HelpIntent")
# This intent is if the user asks the covid hub for help
def help():
    print("Help intent at --> {}".format(datetime.now()))
    return statement("Okay, it's good you asked for help. To ask the latest statistics, say: global stats. Or for stats in a specific country, say: stats in (and then the specific country's name). Furthermore, for latests global covid-19 news, say: global news. Or for updates in a specific country say: latest news (and then the specific country's name). Go ahead, try it out, say alexa ask the covid kid: (and then anything you want to say!).")

@ask.intent("AMAZON.StopIntent")
# This intent is if the user wishes to stop
def stop():
    print("Stop intent at --> {}".format(datetime.now()))
    return statement("Well then, goodbye! Come back again for the most reliable covid-19 statistics and news.")

@ask.intent("AMAZON.NavigateHomeIntent")
def navigate_home():
    print("NavigateHome intent at --> {}".format(datetime.now()))
    return statement("Going home, roger that! I don't understand how, because you have already been quarantined at home, but ok! Goodbye!")

""" BUILTINS """

if __name__ == "__main__":
    app.run(debug=True)
