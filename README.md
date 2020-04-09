# CoronaBot
CoronaBot is a Telegram bot that helps people visualize the impact of COVID-19 with numbers and graphics.

You can get total cases:


![Peru total cases graphic](https://i.imgur.com/ZGEOG8k.jpg)

New confirmed cases:

![Spain new confirmed cases](https://i.imgur.com/a6ztaKz.jpg)

Death numbers:

![Japan death numbers](https://i.imgur.com/kWjDkG0.jpg)

And recovered numbers:

![Canada recovered numbers](https://i.imgur.com/QRdeFAv.jpg)



Just write to @SARS_CoV_2_bot on Telegram or add it to any chat you want.

Simply type: `Coronabot: <command>, <country>, <days_back>`

Where
`<command>` is one of:

    total: for total cases over time
    new: for new cases over time
    deaths: for deaths over time
    recovered: for recovered numbers over time

`<country>` is the name of the country you want to ask for

`<days_back>` (works with `total` only) reflects the reality from as many days ago (max. 7) as you specify

For example:

    Coronabot: total, Brazil, 3
    Coronabot: recovered, japan
    Coronabot: deaths, United Kingdom
