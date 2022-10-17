# Data on Poverty by *Our World in Data*

A global dataset of poverty and inequality measures prepared by [*Our World in Data*](https://ourworldindata.org/poverty) from the World Bank's Poverty and Inequality Platform database.

TODO: Check that link to poverty page works.
TODO: Finish description.

## The complete *Our World in Data* Poverty dataset

### 🗂️ Download our complete PIP dataset : [CSV](https://nyc3.digitaloceanspaces.com/owid-public/data/poverty/pip_dataset.csv) | [XLSX](https://nyc3.digitaloceanspaces.com/owid-public/data/poverty/pip_dataset.xlsx) | [JSON](https://nyc3.digitaloceanspaces.com/owid-public/data/poverty/pip_dataset.json)

TODO: Check that links work.

The CSV and XLSX files follow a format of 1 row per location and year. The JSON version is split by country, with an array of yearly records.

We will continue to publish updated data on poverty as it becomes available. Most metrics are published on an annual basis.

A [full codebook](https://github.com/owid/poverty-data/blob/master/pip-codebook.csv) is made available, with a description for each variable in the dataset.

### About this data

#### Where is this data sourced from?

This data explorer is collated and adapted from the World Bank's [Poverty and Inequality Platform](https://pip.worldbank.org/home) (PIP).

The World Bank's PIP data is a large collection of household surveys where steps have been taken by the World Bank to harmonize definitions and methods across countries and over time.

You can find all the code Our World in Data used to prepare this dataset in [GitHub](https://github.com/owid/poverty-data/blob/master/main.py).

#### About the comparability of household surveys

There is no global survey of incomes. To understand how incomes across the world compare, researchers need to rely on available national surveys.

Such surveys are designed with cross-country comparability in mind, but because the surveys reflect the circumstances and priorities of individual countries at the time of the survey, there are some important differences.

**Income vs expenditure surveys**

One important issue is that the survey data included within the [PIP](https://pip.worldbank.org/home) database tends to measure people's income in high-income countries, and people's consumption expenditure in poorer countries. The two concepts are closely related: the income of a household equals their consumption plus any saving (or minus any borrowing). But they can nonetheless give quite different indications of households' welfare, especially among richer households who tend to save more, or older households that are dissaving in retirement.

In our Data Explorer of this data there is the option to view income and consumption data for individual countries separately, or instead to pool the data available from both types of survey -- which yields greater coverage.

**Other comparability issues**

There are a number of other ways in which comparability across surveys can be limited. The PIP [Methodology Handbook](https://worldbank.github.io/PIP-Methodology/index.html) provides a good summary of the comparability and data quality issues affecting this data and how it tries to address them.

In collating this survey data the World Bank takes a range of steps to harmonize it where possible, but comparability issues remain. These affect comparisons both across countries and within individual countries over time.

To help communicate the latter, the World Bank produces a variable that groups surveys within each individual country into more comparable 'spells'. Our Data Explorer provides the option of viewing the data with these breaks in comparability indicated. 

#### Global and regional poverty estimates

Along with data for individual countries derived from household surveys, the World Bank also provides global and regional poverty estimates. Since surveys are not conducted annually in every country, in order to produce these aggregate estimates for a given year, the World Bank takes the surveys falling closest to that year for each country and 'lines-up' the data to the year being estimated by projecting it forwards or backwards.

This lining-up is generally done on the assumption that household incomes or expenditure grow in line with the growth rates observed in national accounts data. You can read more about the interpolation methods used by the World Bank in [Chapter 5](https://worldbank.github.io/PIP-Methodology/lineupestimates.html) of the Poverty and Inequality Platform Methodology Handbook.


#### How does the data account for inflation and for differences in the cost of living across countries?

To account for inflation and price differences across countries, the data is measured in 2011 and 2017 international-\$.

The international-\$ is a hypothetical currency that results from price adjustments across time and place. It is defined as having the same purchasing power as one US-\$ would in the United States in a given base year -- in this case 2011 and 2017. One int.-\$ buys the same quantity of goods and services no matter where or when it is spent.

There are many challenges to making such adjustments and they are far from perfect. Angus Deaton ([Deaton, 2010](https://rpds.princeton.edu/sites/g/files/toruqf1956/files/media/deaton_price_indexes_inequality_and_the_measurement_of_world_poverty_aer.pdf)) provides a good discussion of the difficulties involved in price adjustments and how this relates to global poverty measurement.

But in a world where price differences across countries and over time are large it is important to attempt to account for these differences as well as possible, and this is what these adjustments do.

#### Absolute vs relative poverty lines

This dataset provides poverty estimates for a range of absolute and relative poverty lines.

An absolute poverty line represents a fixed standard of living; a threshold that is held constant across time. Within the World Bank's poverty data, absolute poverty lines also aim to represent a standard of living that is fixed across countries (by converting local currencies to international-\$). The International Poverty Line of \$1.90 per day is the best known absolute poverty line and is used by the World Bank and the UN to measure extreme poverty around the world.

Relative poverty lines instead rise and fall in absolute terms as average incomes change within a given country. In most cases they are set at a certain fraction of the median income. Because of this, relative poverty can be considered a metric of inequality -- it measures how spread out the bottom half of the income distribution is.

The idea behind measuring poverty in relative terms is that a person's well-being depends not on their own absolute standard of living but on how that standard compares with some reference group, or whether it enables them to participate in the norms and customs of their society. For instance, joining a friend's birthday celebration without shame might require more resources in a rich society if the norm is to go for an expensive meal out, or give costly presents.

Our dataset includes three commonly-used relative poverty lines: 40%, 50%, and 60% of the median.

Such lines are most commonly used in rich countries, and are the main way poverty is measured by the [OECD](https://data.oecd.org/inequality/poverty-rate.htm) and the [European Union](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Glossary:At-risk-of-poverty_rate).\
\
More recently, relative poverty measures have come to be applied in a global context. The share of people living below 50 per cent of median income is, for instance, one of the UN's [Sustainable Development Goal indicators](https://sdg-tracker.org/inequality#10.2). And the World Bank now produces estimates of global poverty using a [Societal Poverty Line](https://datatopics.worldbank.org/world-development-indicators/stories/societal-poverty-a-global-measure-of-relative-poverty.html) that combines absolute and relative components.

When comparing relative poverty rates around the world, however, it is important to keep in mind that -- since [average incomes](https://ourworldindata.org/explorers/poverty-explorer?tab=map&facet=none&hideControls=false&Metric=Median&Poverty+line=%241.90+a+day&Household+survey+data+type=Show+data+from+both+income+and+expenditure+surveys&country=IND~MOZ~BRA~MDG~GHA) are so far apart -- such relative poverty lines relate to very different standards of living in rich and poor countries.

#### Does the data account for non-market income, such as food grown by subsistence farmers?

Many poor people today, as in the past, rely on subsistence farming rather than a monetary income gained from selling goods or their labor on the market. To take this into account and make a fair comparison of their living standards, the statisticians that produce these figures estimate the monetary value of their home production and add it to their income/expenditure.

## Changelog

- On October 14, 2022: The first version of the World Bank Poverty and Inequality Platform (PIP) dataset was made available.

## Data alterations

- **We standardize names of countries and regions.** Since the names of countries and regions are different in different data sources, we harmonize all names to the [*Our World in Data* standard entity names](https://ourworldindata.org/world-region-map-definitions).

TODO: Complete list of data alterations.

## License

All visualizations, data, and code produced by _Our World in Data_ are completely open access under the [Creative Commons BY license](https://creativecommons.org/licenses/by/4.0/). You have the permission to use, distribute, and reproduce these in any medium, provided the source and authors are credited.

The data produced by third parties and made available by _Our World in Data_ is subject to the license terms from the original third-party authors. We will always indicate the original source of the data in our database, and you should always check the license of any such third-party data before use.

## Authors

This data has been collected, aggregated, and documented by Joe Hasell and Pablo Arriagada.

TODO: Check if this list is complete.

*Our World in Data* makes data and research on the world’s largest problems understandable and accessible. [Read more about our mission](https://ourworldindata.org/about).
