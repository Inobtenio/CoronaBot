import inspect
import logging
from plotter import CommandPlotter, CommandError, CountryError, DaysError, PlottingError

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseBot(object):
    def start_text(self):
        text =  """Hi, I'm the CoronaBot. You can ask for current info about the novel coronavirus in your area.

                Just type: Coronabot: <command>, <country>, <days_back>

                Where
                <command> is one of:
                    'total' for total cases over time
                    'new' for new cases over time
                    'deaths' for deaths over time
                    'recovered' for recovered numbers over time

                <country> is the name of the country you want to ask for

                <days_back> (works with 'total' only) reflects the reality from as many days ago (max. 7) as you specify

                For example:
                    Coronabot: total, Brazil, 3
                    Coronabot: recovered, japan

                Safe plotting ;)"""

        return inspect.cleandoc(text)

    def info_text(self):
        text =  """Created by:
                Kevin Martin
                https://github.com/Inobtenio
                https://twitter.com/Inobtenio

                Powered by:
                Johns Hopkins CSSE (https://github.com/CSSEGISandData/COVID-19)
                Coronavirus Tracker (https://thevirustracker.com)
                COVID API by Javier Aviles (https://github.com/javieraviles/covidAPI)

                Open source code at:
                https://github.com/Inobtenio/CoronaBot
                """

        return inspect.cleandoc(text)

    def get_plot_file_url(self, options, **kwargs):
        try:
            return CommandPlotter().execute(options['command'], options['country'], options['days'])
        except (CommandError, CountryError, DaysError, PlottingError) as error:
            self.handle_plot_error(error_message=str(error), bot_info=kwargs)

    def handle_plot_error(self, **kwargs):
        raise NotImplementedError

    def log_error(self, message):
        logger.error(message)
