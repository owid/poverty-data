# Data on Poverty by the World Bank Poverty and Inequality Platform

A global dataset of poverty and inequality measures prepared by [*Our World in Data*](https://ourworldindata.org/poverty) from the World Bank's Poverty and Inequality Platform (PIP) database.

## About this data

#### Where is this data sourced from?

This data explorer is collated and adapted from the World Bank’s [Poverty and Inequality Platform](https://pip.worldbank.org/home) (PIP).

The World Bank’s PIP data is a large collection of household surveys where steps have been taken by the World Bank to harmonize definitions and methods across countries and over time.

#### About the comparability of household surveys

There is no global survey of incomes. To understand how incomes across the world compare, researchers need to rely on available national surveys.

Such surveys are partly designed with cross-country comparability in mind, but because the surveys reflect the circumstances and priorities of individual countries at the time of the survey, there are some important differences.

**Income vs expenditure surveys**

One important issue is that the survey data included within the [PIP](https://pip.worldbank.org/home) database tends to measure people’s income in high-income countries, and people’s consumption expenditure in poorer countries.

The two concepts are closely related: a household's income equals their consumption plus any saving, or minus any borrowing or spending out of savings. 

One important difference is that, while zero consumption is not a feasible value – people with zero consumption would starve – a zero income is a possible value. This means that, at the bottom end of the distribution, income and consumption can give quite different pictures of a person’s welfare. For instance, a person dissaving in retirement may have a very low, or even zero, income, but have a high level of consumption nevertheless.

The gap between income and consumption is higher at the top of this distribution too, richer households tend to save more, meaning that the gap between income and consumption is higher at the top of this distribution too. Taken together, one implication is that inequality measured in terms of consumption is generally somewhat lower than the inequality measured in terms of income.

In our [Data Explorer](https://ourworldindata.org/poverty#explore-data-poverty) of this data, there is the option to view only income survey data or only consumption survey data, or instead to pool the data available from both types of survey – which yields greater coverage.

**Other comparability issues**

There are a number of other ways in which comparability across surveys can be limited. The PIP [Methodology Handbook](https://datanalytics.worldbank.org/PIP-Methodology/) provides a good summary of the comparability and data quality issues affecting this data and how it tries to address them.

In collating this survey data the World Bank takes a range of steps to harmonize it where possible, but comparability issues remain. These affect comparisons both across countries and within individual countries over time.

To help communicate the latter, the World Bank produces a variable that groups surveys within each individual country into more comparable ‘spells’. Our [Data Explorer](http://ourworldindata.org/poverty#explore-data-poverty) provides the option of viewing the data with these breaks in comparability indicated, and these spells are also indicated in our data [download](https://github.com/owid/poverty-data).

#### Global and regional poverty estimates

Along with data for individual countries, the World Bank also provides global and regional poverty estimates which aggregate over the available country data.

Surveys are not conducted annually in every country however – coverage is generally poorer the further back in time you look and remains particularly patchy within Sub-Saharan Africa. You can see that visualized in our chart of the [number of surveys included in the World Bank data](https://ourworldindata.org/grapher/data-deprivation-poverty-surveys-per-decade?time=latest) by decade.

In order to produce global and regional aggregate estimates for a given year, the World Bank takes the surveys falling closest to that year for each country and ‘lines up’ the data to the year being estimated by projecting it forward or backward.

This lining-up is generally done on the assumption that household incomes or expenditure grow in line with the growth rates observed in national accounts data. You can read more about the interpolation methods used by the World Bank in [Chapter 5](https://datanalytics.worldbank.org/PIP-Methodology/lineupestimates.html) of the Poverty and Inequality Platform Methodology Handbook.

#### How does the data account for inflation and for differences in the cost of living across countries?

To account for inflation and price differences across countries, the World Bank’s data is measured in international dollars. This is a hypothetical currency that results from price adjustments across time and place. It is defined as having the same purchasing power as one US-$ would in the United States in a given base year. One int.-$ buys the same quantity of goods and services no matter where or when it is spent.

There are many challenges to making such adjustments and they are far from perfect. Angus Deaton ([Deaton, 2010](https://rpds.princeton.edu/sites/g/files/toruqf1956/files/media/deaton_price_indexes_inequality_and_the_measurement_of_world_poverty_aer.pdf)) provides a good discussion of the difficulties involved in price adjustments and how this relates to global poverty measurement.

But in a world where price differences across countries and over time are large, it is important to attempt to account for these differences as well as possible, and this is what these adjustments do.

In September 2022, the World Bank updated its methodology, and now uses international-$ expressed in 2017 prices – updated from 2011 prices. This has had little effect on our overall understanding of poverty and inequality around the world. But poverty estimates for particular countries vary somewhat between the old and updated methodology. You can read more about this update in our article _[From $1.90 to $2.15 a day: the updated International Poverty Line](https://ourworldindata.org/from-1-90-to-2-15-a-day-the-updated-international-poverty-line)_.

To allow for comparisons with the official data now expressed in 2017 international-$ data, the World Bank continues to release its poverty and inequality data expressed in 2011 international-$ as well. We have built a [Data Explorer](https://ourworldindata.org/explorers/poverty-explorer-2011-vs-2017-ppp) to allow you to compare these, and we make all figures available in terms of both sets of prices in our [data download](https://github.com/owid/poverty-data).

#### Absolute vs relative poverty lines

This dataset provides poverty estimates for a range of absolute and relative poverty lines.

An absolute poverty line represents a fixed standard of living; a threshold that is held constant across time. Within the World Bank’s poverty data, absolute poverty lines also aim to represent a standard of living that is fixed across countries (by converting local currencies to international-\$). The International Poverty Line of \$2.15 per day (in 2017 international-\$) is the best-known absolute poverty line and is used by the World Bank and the UN to measure extreme poverty around the world.

The value of relative poverty lines instead rises and falls as average incomes change within a given country. In most cases, they are set at a certain fraction of the median income. Because of this, relative poverty can be considered a metric of inequality – it measures how spread out the bottom half of the income distribution is.

The idea behind measuring poverty in relative terms is that a person’s well-being depends not on their own absolute standard of living but on how that standard compares with some reference group, or whether it enables them to participate in the norms and customs of their society. For instance, joining a friend’s birthday celebration without shame might require more resources in a rich society if the norm is to go for an expensive meal out, or give costly presents.

Our dataset includes three commonly-used relative poverty lines: 40%, 50%, and 60% of the median.

Such lines are most commonly used in rich countries, and are the main way poverty is measured by the [OECD](https://data.oecd.org/inequality/poverty-rate.htm) and the [European Union](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Glossary:At-risk-of-poverty_rate).

More recently, relative poverty measures have come to be applied in a global context. The share of people living below 50% of the median income is, for instance, one of the UN’s [Sustainable Development Goal indicators](https://sdg-tracker.org/inequality#10.2). And the World Bank now produces estimates of global poverty using a [Societal Poverty Line](https://datatopics.worldbank.org/world-development-indicators/stories/societal-poverty-a-global-measure-of-relative-poverty.html) that combines absolute and relative components.

When comparing relative poverty rates around the world, however, it is important to keep in mind that – since [average incomes](https://ourworldindata.org/explorers/poverty-explorer?tab=map&facet=none&hideControls=false&Metric=Median+income+or+expenditure&Household+survey+data+type=Show+data+from+both+income+and+expenditure+surveys&country=IND~MOZ~BRA~MDG~GHA) are so far apart – such relative poverty lines relate to very different standards of living in rich and poor countries.

#### Does the data account for non-market income, such as food grown by subsistence farmers?

Many poor people today, as in the past, rely on subsistence farming rather than a monetary income gained from selling goods or their labor on the market. To take this into account and make a fair comparison of their living standards, the statisticians that produce these figures estimate the monetary value of their home production and add it to their income/expenditure.

## Data alterations

- **We standardize the names of countries and regions.** Since the names of countries and regions are different in different data sources, we harmonize all names to the [*Our World in Data* standard entity names](https://ourworldindata.org/world-region-map-definitions).

- **We generate decile thresholds and amend missing medians.** Distributional data is generated by merging thousands of queries that generate decile thresholds and fill missing median data in countries like China, India at Indonesia at the national level.

- **We include relative poverty estimates.** Relative poverty is estimated by calculating the 40%, 50%, and 60% of the median of each row and using that number as a poverty line in a new query.

## Changelog

- On October 17, 2022: The repository is restructured and some minor issues are fixed.
- On October 14, 2022: The first version of the World Bank Poverty and Inequality Platform (PIP) dataset was made available.

## License

All visualizations, data, and code produced by _Our World in Data_ are completely open access under the [Creative Commons BY license](https://creativecommons.org/licenses/by/4.0/). You have the permission to use, distribute, and reproduce these in any medium, provided the source and authors are credited.

The data produced by third parties and made available by _Our World in Data_ is subject to the license terms from the original third-party authors. We will always indicate the original source of the data in our database, and you should always check the license of any such third-party data before use.

## Authors

This data has been collected, aggregated, and documented by Joe Hasell and Pablo Arriagada.

*Our World in Data* makes data and research on the world’s largest problems understandable and accessible. [Read more about our mission](https://ourworldindata.org/about).
