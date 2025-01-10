# Urban Activity Atlas

The Urban Activity Atlas is a visual representation of geographic variation in human activity within North American metropolitan regions.

The geographic units in the map are 6-digit [*geohashes*](https://en.wikipedia.org/wiki/Geohash) that overlap with the largest 300 metropolitan regions - in terms of population - in the United States (census data from 2022) and Canada (2021). You can explore geohashes [here](https://geohash.softeng.co/).

The data shown in the map are from [Spectus](https://spectus.ai/) and represent the total number of *stops* in a full year: April 1, 2023 to March 31, 2024. These stops, which are measured using mobile devices like cell phones, "represent the points at which devices spend time, and are built according to the spatial and temporal proximity of individual device pings" [Spectus](https://spectus.ai/glossary/).

Each map in the Urban Activity Atlas shows a gradient of activity levels, i.e., the total number of stops, for the selected metropolitan region. [COLOR 1] areas experienced the least amount of activity in the region between April 2023 and March 2024, and [COLOR 2] areas experienced the most. Activity levels are standardized for each respective region, with values representing the total number of stops in the geohash divided by the total number of stops in the region overall. Therefore, activity levels should only be compared *within* regions, not *across* regions.