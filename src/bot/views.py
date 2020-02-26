from datetime import datetime, timedelta
import plotly.graph_objects as go
import pandas as pd

from .exceptions import InvalidArgument, APIError, NotFound
from .rates import api


DEFAULT_BASE = 'USD'
DEFAULT_HISTORY_DAYS = 7


INVALID_ARGUMENTS = "Invalid command arguments. See /help for usage."
NOT_FOUND = "No exchange rate data is available for the selected currency."
INTERNAL_ERROR = "Whoops. Something goes wrong, please try again later."


class ErrorResponseMixin:
    """
    Handle view errors to readable response
    """
    def render(self):
        try:
            response = super().render()
        except InvalidArgument as e:
            response = e.message
        except APIError as e:
            response = e.message
        except Exception as e:
            response = INTERNAL_ERROR
        return response


class View:
    """
    Base command view
    """
    def __init__(self, text=None):
        self._text = text
        self._args = (text or '').split()[1:]

    def args(self):
        """
        Extracts arguments from command message
        """
        return ()

    def render_to_response(self):
        """
        Renders messaget to response
        """
        return NotImplemented()

    def render(self):
        """
        Renders view
        """
        return self.render_to_response()


class ListView(ErrorResponseMixin, View):
    def args(self):
        base = DEFAULT_BASE
        if self._args:
            base, *_ = self._args
        return base.upper(),

    def render_to_response(self):
        latest = api.latest(*self.args())
        rates = latest["rates"]
        return "\n".join(
            f"{currency}: {value}"
            for currency, value in rates.items()
        )


class ExchangeView(ErrorResponseMixin, View):

    def args(self):
        if len(self._args) < 3:
            raise InvalidArgument(INVALID_ARGUMENTS)

        amount, base, currency = None, DEFAULT_BASE, None
        if len(self._args) == 3:
            amount, to, currency = self._args
            if to != 'to':
                base = to
        if len(self._args) > 3:
            amount, base, to, currency, *_ = self._args

        amount = amount.strip("$")

        try:
            amount = float(amount)
        except ValueError:
            raise InvalidArgument(INVALID_ARGUMENTS)

        amount = float(amount)

        return amount, base.upper(), currency.upper()

    def render_to_response(self):
        amount, base, currency = self.args()

        latest = api.latest(base)

        if not latest or not latest.get("rates", None):
            raise NotFound(NOT_FOUND)

        result = latest["rates"][currency] * amount

        return f"{result:.2f}"


class HistoryView(ErrorResponseMixin, View):
    def args(self):
        if len(self._args) < 2:
            raise InvalidArgument(INVALID_ARGUMENTS)

        base, currency, days = DEFAULT_BASE, None, DEFAULT_HISTORY_DAYS
        base, currency, *_, = self._args

        for arg in _:
            if arg.isdigit():
                days = int(arg) - 1
                break

        return base.upper(), currency.upper(), days

    def render_to_response(self):
        base, currency, days = self.args()

        end_at = datetime.now()
        start_at = end_at - timedelta(days=days)

        history = api.history(base, currency, start_at=start_at, end_at=end_at)

        if not history or not history.get("rates", None):
            raise NotFound(NOT_FOUND)

        flat_history = ((k, v[currency]) for k, v in history["rates"].items())
        df = pd.DataFrame(flat_history, columns=['Date', 'Rate']).sort_values('Date')

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.Date,
            y=df.Rate,
            name=f"{base}/{currency}",
            line_color='deepskyblue'
        ))

        return fig.to_image(format='png')
