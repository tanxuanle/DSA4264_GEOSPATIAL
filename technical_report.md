# Technical Report

**Project: Geospatial Analysis: Optimising Public Transport in Singapore**  
**Members: Gayathri d/o Ganesan, Kaitlyn Lai Lin Ching, Liew Xin Yu, Tan Xuan Le**  
Last updated on 5 November 2024.


## Section 1: Context
<div style="text-align: justify">

In recent years, the Land Transport Authority (LTA) has introduced several new MRT lines, such as the Downtown Line and the Thomson-East Coast Line, to enhance the efficiency and appeal of public transport in Singapore. Before these expansions, commuters relied heavily on trunk bus services, which often required longer travel times and were more susceptible to traffic delays.

Initial survey data and anecdotal evidence suggest that ridership on some of these trunk services has declined since the MRT lines became operational. The Ministry of Transport (MOT) aims to streamline bus services to reduce redundancy and encourage commuters to use the expanded MRT network for longer journeys.

In light of these developments, as part of the Data Science Department, we have been tasked with optimising Singapore’s bus routes. This project will use data science methods to assess the current bus network, evaluate overlaps with MRT lines, and identify opportunities for reconfiguration. By optimising bus routes to better support the MRT system, we aim to improve network efficiency, align with commuter demand, and contribute to a more integrated public transport system.

## Section 2: Scope
### 2.1 Problem
The key business problem we are trying to solve through this project is identifying trunk services that have substantial overlap with MRT lines, to prioritise for consideration for partial or complete removal. In particular, we are looking for bus routes that significantly overlap with the newer MRT lines, which are the Downtown Line (DTL) as well as the Thomson-East Coast Line (TEL). This will streamline public transportation, minimise redundancy, and improve operational efficiency.

The main stakeholder is MOT’s Land Division, specifically the Public Transportation team which oversees the overall planning of public transportation routes and finds ways to optimise them for cost and coverage. LTA, as the organisation in charge of implementing and operationalising these bus and MRT services, is another key stakeholder. The public also stands to benefit from this optimisation, as these changes aim to enhance their commuting experience by providing a more efficient network that reduces travel time and improves service coverage.

Without optimising these bus routes, the limited budget for public transportation subsidies cannot be efficiently allocated to serve emerging areas of demand or to improve service frequency in underserved areas. Currently, trunk bus services that overlap with MRT lines contribute to redundant operational costs. By strategically removing these overlapping services, MOT and LTA could redirect the saved resources to implementing new routes, meeting commuter demand where it is most needed.

Data science is essential for tackling this problem, as manually analysing route overlaps with MRT lines is time-consuming, prone to errors, and limited in scalability. Using data science, we can automate the identification of overlapping segments by analysing spatial data for both bus routes and MRT lines. Additionally, with data science, we will be able to consider other factors that may contribute to the public response to a proposed change in routes, such as passenger demand and availability of alternative routes. This allows for a more nuanced approach to optimising the network in a way that anticipates public needs. Furthermore, we can extend this analysis to future MRT lines that are being released, allowing continued refinement of bus routes based on updated data.


### 2.2 Success Criteria

Success in this project would be identifying 2 to 3 bus routes that can be streamlined by partial or full removal. This would align bus services more closely with current demand patterns and complement the expanded MRT network. By reducing redundancy in trunk services, we aim to increase the efficiency of the public transport system.

The resources saved from the streamlined routes can then be reallocated to implement other routes that serve underserved areas, such as in areas where MRT coverage remains limited. This would improve accessibility across Singapore, and increase convenience for all commuters.


### 2.3 Assumptions

For our project, we focused on identifying bus routes that significantly overlapped with the newer MRT lines — the DTL and TEL — as we assumed that bus routes significantly overlapping with the older MRT lines would have already been identified and addressed by LTA. However, the analysis can still be applied to identify redundancies with other lines if needed.

We also assumed that commuters with similar travel times and transfer requirements between bus and MRT options are likely to be indifferent between the two modes. This suggests that redundant bus routes could be removed or rerouted without significantly impacting commuter experience. This assumption, however, does not fully account for non-quantifiable factors such as commuter preference, perceived convenience, or accessibility considerations. 

Another assumption we made for this project was that there is enough manpower to conduct a detailed review of each bus route identified after using our scoring framework. This would include analysing and evaluating which portions of the bus routes can be removed, as well as planning a more efficient reroute of the selected bus routes.


## Section 3: Methodology

### 3.1 Technical Assumptions

#### 3.1.1 Key Hypotheses of Interest

To complement the expanded MRT network, we aim to optimise Singapore’s bus routes to improve connectivity and public resource allocation. The following hypotheses were written to guide our analysis. 

1. The proximity of MRT lines reduces bus demand.
2. Reducing overlapping bus services will increase MRT usage.
3. Optimising bus routes will improve public transport network efficiency.

In our project, we also assume a walkable distance of 400 metres between MRT stations and bus stops, such that any bus routes that are within this distance are considered functionally parallel.

#### 3.1.2 Data Availability and Gaps

We made use of publicly available data mainly from LTA DataMall and OneMap, as they are reliable sources from the Singapore government. We assumed that the datasets retrieved were updated timely and consistent. 

However, due to the lack of access to advanced map-matching tools, route alignment is done based on geographic coordinates. Without precise mapping, there might be minor deviations in determining the exact overlaps between bus routes and MRT lines. Also, there is a lack of service-specific passenger data. To handle this, we carefully processed the passenger data (discussed in section 3.1.3.) before using it for our analysis. 

#### 3.1.3 Averaging for Passenger Demand

To estimate the passenger demand for each bus service at each stop, we assumed that demand is distributed evenly across services at each bus stop. We averaged the number of passengers for each bus service by dividing the passenger volume at each stop by the number of bus services

### 3.2 Data

#### 3.2.1 Data Sources

As mentioned above, we leveraged publicly available datasets from the LTA DataMall and OneMap to perform a comprehensive analysis of overlaps between bus and MRT routes. The main datasets include the **bus stops** and **bus routes** datasets from LTA DataMall, which provides detailed information on bus service routes, stop sequences and schedules. This data is essential for mapping bus routes and understanding the structure of Singapore’s bus network.

To support our analysis of public receptivity and demand, we retrieved and processed the passenger volume data, which contained the tap-in and tap-out counts at each bus stop. This dataset enables us to analyse demand patterns across different stops and bus services, helping us to study the possible effects of removing or modifying a bus route. 

Additionally, to support our geospatial analysis and visualisations, we used the OneMap API to obtain geographic coordinates of MRT stations. This enables us to measure the proximity between bus stops and MRT stations, which is important for determining overlapping bus routes.

#### 3.2.2 Data Retrieval and Processing

Data retrieval was conducted through API calls to LTA DataMall and OneMap, where personal access tokens were required for secure access. Following best practices, we stored our API keys in a .env file to ensure security. Key functions were also written to automate data retrieval and storage. 

Firstly, we created several functions to streamline API requests and data handling. For instance, *fetch_data*, *save_to_csv*, and *download_file* were meant to send requests and save the response for easy access. As some of the responses return a download link instead of the dataset, download_file is used for the retrieval of such datasets. 

Then, we created customised functions for each dataset we wanted to retrieve. An example would be the *get_bus_routes* function which sends a request to LTA DataMall each time it is called. The function includes the headers, parameters, and URL required to make the API call as specified in the documentation. Due to API call limits imposed by the platform, pagination handling was also included to retrieve all pages of data smoothly.

All retrieved datasets were saved in .csv format in a structured */data* folder. This organisation enables us to access the data easily when we conduct our analysis. 

To facilitate our analysis, we merged the bus routes and bus stops dataset into the **bus_routes_full_combined.csv** file using *pd.merge()*, so that the dataset consists of both the geographic coordinates and the stop sequences. 


### 3.3 Experimental Design
#### 3.3.1 Calculating overlap between bus routes and MRT lines

We began by transforming all relevant bus routes, along with the DTL and TEL MRT services, into geospatial objects to facilitate accurate spatial analysis. To represent the bus routes and MRT lines as polylines, we first sorted the bus stop data by their StopSequence and the MRT station data by both LINE and STN_NO. For the bus routes, we grouped the sorted data by ServiceNo and Direction, constructing LineString geometries for each route using the ordered Point geometries of the bus stops. Since we are focusing on trunk services, we filtered this data, creating a specific dataset, trunk_routes_ls, that includes only these primary routes for use in our overlap calculations. Similarly, we filtered the MRT station data to focus on the DTL and TEL, creating LineString geometries for these MRT lines using the corresponding ordered Point geometries of the MRT stations.

Both LineString geometries were encapsulated within new GeoDataFrames, with their Coordinate Reference System (CRS) set to "EPSG:4326" to accurately read in the coordinates that are in the global latitude-longitude format. To assess bus route accessibility to MRT services, we established a 400-metre buffer along each MRT polyline, reflecting the typical walking distance passengers are willing to walk to access public transit. This buffer method generated polygon geometries representing the areas surrounding the MRT lines, which were used to identify the overlaps with the bus routes. 

For precise calculations of the geospatial intersections, we converted both the bus route and buffered MRT line geometries to the EPSG:32648 Coordinate Reference System, which supports accurate distance measurements. We calculated two key metrics for each bus route’s overlap with the MRT buffers: the overlap length, representing the total intersecting distance, and the overlap percentage, the proportion of the bus route within the buffer zone. Sorting the bus routes by overlap length, we identified the top 10 bus routes with the greatest overlap length with either the DTL or TEL. We chose to prioritise overlap length over percentage for route comparison to eliminate shorter bus routes with high overlap percentages. This focus on length allowed us to target longer trunk services that connect broader areas across the island, essential for evaluating cross-island connectivity in comparison to combined bus and MRT journeys. 

#### 3.3.2 Evaluating factors likely to affect public response

In addition to using overlap length to determine which bus routes to remove or partially adjust, we considered several factors which are likely to influence public response to these changes. We identified three key considerations: the number of passengers affected by the route removal, the availability of alternative bus routes that cover portions of the removed route, and the availability of nearby MRT stations that offer an alternative mode of travel. 

**1. Passenger Impact** 

To estimate the number of passengers affected by the removal of specific bus routes, we calculated the average tap-in and tap-out volumes for each bus service at individual bus stops. We began by determining the average tap volume at each bus stop, which we achieved by dividing the total tap volumes by the number of bus services that serve that stop. This method relies on the assumption that tap volumes are evenly distributed across all bus services at each stop, a limitation we acknowledge due to data constraints.

Next, we aggregated the average tap volumes across all bus stops along each bus route. By summing the average tap volumes for each stop and dividing by the total number of stops on the route, we obtained a reasonable estimate of passenger demand for each bus service.

This estimated demand for the ten shortlisted bus services was then incorporated into our scoring framework. This allows us to evaluate the potential number of passengers who would be affected by the removal of these routes, providing critical insights for decision-making.

**2. Availability of alternative bus routes**  

To estimate the availability of alternative bus routes that could cover portions of the proposed route removals, we analysed the number of bus routes that overlap with our top ten shortlisted services. We calculated the geospatial intersection between each shortlisted bus service and all other bus routes. If the overlap percentage between a shortlisted route and another bus route exceeds 30%, we consider them as overlapping.

We selected a 30% threshold because it indicates a significant portion of the route, suggesting that alternative bus services effectively cover substantial parts of the journey. A higher threshold would yield very few overlapping routes, limiting our analysis and potentially overlooking viable alternatives.

By applying this criterion, we aimed to identify bus routes with existing alternatives for sections of the journey. This approach is essential for minimising disruption to passengers in the event of route removals. 

**3. Proximity to MRT stations**

To estimate the availability of nearby MRT stations along the bus routes, we assessed the proximity of bus stops to MRT stations within a 400-metre radius. We calculated the number of bus stops located within this buffer around each MRT station, allowing us to determine how many bus stops along each route are conveniently positioned near alternative transport options.

By dividing the count of bus stops near MRT stations by the total number of bus stops on each route, we obtained a percentage that reflects the proportion of stops with easy access to MRT services. We chose the 400-metre distance based on its general acceptance as a reasonable walking distance for passengers seeking alternative transport.

This metric is crucial for evaluating how easily passengers can access the MRT system in the event of bus route removals. It helps ensure that there are nearby, viable alternatives for commuters, thereby minimising disruption and maintaining connectivity in the public transportation network.

#### 3.3.3 Developing a scoring framework to prioritise bus route removals

To systematically rank the shortlisted bus routes, we developed a scoring framework based on four key metrics: overlap percentage with MRT lines, average tap volume, number of overlapping bus services, and percentage of bus stops near MRT stations. We selected overlap percentage over overlap length as a key metric because it offers a more comprehensive assessment of route redundancy by accounting for the proportion of the route that overlaps with MRT lines, rather than just the absolute overlap distance and it is assumed that shorter, redundant routes have already been filtered out. Average tap volume reflects passenger demand, prioritising routes with lower ridership for possible removal. The number of overlapping bus services provides insight into alternative route availability, indicating whether other bus routes could cover the affected areas. Finally, the percentage of bus stops near MRT stations helps evaluate whether passengers would have accessible alternative transportation if the bus route were to be removed.

We applied min-max normalisation to standardise the range for each metric, scaling values to a range between 0 and 1. This allows each metric to contribute proportionally to the overall score, regardless of its original unit or range. For average tap volume, we inverted the scaling so that routes with higher passenger demand received a lower score. This inversion prioritises routes with fewer passengers for potential adjustment, as these would impact fewer users.

After normalisation, we assigned weights to each metric based on its importance in indicating route redundancy and accessibility to alternative transportation. We weighted overlap percentage the highest (5), as it directly measures the proportion of the route that overlaps with other services, signifying potential redundancy. Average tap volume and overlapping bus services count were weighted at 2 respectively to prioritise services with lower passenger demand and more alternative transport options. Lastly, the percentage of bus stops near MRT was weighted at 1 to account for the accessibility to MRT services should there be no alternative bus routes when the selected bus route is removed.

Finally, we computed a composite score for each route by taking a weighted sum of the normalised values for each metric. Sorting the bus services by their composite score allowed us to rank them in terms of suitability for potential route removal, with higher scores indicating routes with higher overlap, fewer passengers, and greater proximity to alternative bus routes and MRT stations. To select the final three bus routes for partial or complete removal, we chose the top 4 bus routes with the highest scores.


## Section 4: Findings

### 4.1 Results

After applying our scoring framework to the top 10 shortlisted bus services, we identified Bus 67, 23, 65 and 170 as having the highest overall scores.

To understand the potential impact of removing or rerouting these services, we conducted further analysis of how passengers might be affected. The table below presents our findings: *Overall Score* indicates each service’s ranking based on our scoring framework, *Origin* shows the origin points for each bus route’s analysis, *Destination* highlights destinations along each bus route with high average tap-in and tap-out volumes, *Time Savings* shows the time passengers could save by switching to MRT instead of taking the bus directly, and Within Buffer indicates if the destinations are within the 400m MRT buffer or not. 

<div style="text-align: center">

<table>
  <tr>
    <th>Service Number</th><th>Overall Score</th><th>Origin</th><th>Destination</th><th>Time Savings (mins)</th><th>Within Buffer</th>
  </tr>
  <tr>
    <td rowspan="3">67</td>
    <td rowspan="3">5.98</td>
    <td rowspan="3">Choa Chu Kang Interchange</td>
    <td>Bukit Panjang</td><td>NIL</td><td>Yes</td>
  </tr>
  <tr>
    <td>Beauty World</td><td>9</td><td>Yes</td>
  </tr>
  <tr>
    <td>Little India</td><td>23</td><td>Yes</td>
  </tr>
  <tr>
    <td rowspan="4">23</td>
    <td rowspan="4">5.65</td>
    <td rowspan="4">Tampines West</td>
    <td>Boon Keng</td><td>NIL</td><td>Yes</td>
  </tr>
  <tr>
    <td>Rochor</td><td>3</td><td>Yes</td>
  </tr>
  <tr>
    <td>Bendemeer</td><td>NIL</td><td>No</td>
  </tr>
  <tr>
    <td>Litte India</td><td>3</td><td>Yes</td>
  </tr>
  <tr>
    <td rowspan="7">65</td>
    <td rowspan="7">5.61</td>
    <td rowspan="5">Tampines Interchange</td>
    <td>Ubi</td><td>13</td><td>Yes</td>
  </tr>
  <tr>
    <td>Macpherson</td><td>14</td><td>No</td>
  </tr>
  <tr>
    <td>Boon Keng</td><td>14</td><td>Yes</td>
  </tr>
  <tr>
    <td>River Valley</td><td>36</td><td>No</td>
  </tr>
  <tr>
    <td>Harbourfront</td><td>64</td><td>No</td>
  </tr>
  <tr>
    <td rowspan="2">Bencoolen MRT Station</td>
    <td>River Valley</td><td>2</td><td>No</td>
  </tr>
  <tr>
    <td>Harbourfront</td><td>21</td><td>No</td>
  </tr>
  <tr>
    <td rowspan="3">170</td><td rowspan="3">5.23</td>
    <td rowspan="3">Little India MRT Station</td>
    <td>Botanic Gardens</td><td>14</td><td>Yes</td>
  </tr>
  <tr>
    <td>King Albert Park</td>
    <td>15</td>
    <td>Yes</td>
  </tr>
  <tr>
    <td>Hillview</td>
    <td>20</td>
    <td>Yes</td>
  </tr>
</table>
</div>

### 4.2 Discussion

Our analysis revealed that Bus 23, despite showing a high percentage of overlap with the DTL buffer, offers significantly lower time savings compared to other identified routes. Upon closer inspection, we found that this overlap primarily occurs along an express sector on the Pan-Island Expressway (PIE). In contrast, key residential areas along the Bus 23 route, such as Bedok Reservoir and Whampoa/Bendemeer, lie outside the DTL buffer.

As a result, switching from Bus 23 to the DTL would offer minimal to no time savings for most passengers, making it unlikely that they would opt for the MRT alternative. Removing this route could therefore lead to high public dissatisfaction, as it would disrupt direct connections without offering a viable, time-efficient alternative. Given these findings, we decided to proceed with the potential removal of the 3 other bus routes — 67, 65, and 170 — which demonstrate significant time savings. 

Before discussing the implications of our results, we will provide some context for each bus service. Bus 67 is a trunk route operating from Choa Chu Kang Interchange to Tampines Interchange every day, passing through Bukit Timah, Little India, and Geylang. Its main overlap with the Downtown Line is from Bukit Panjang MRT Station to Little India MRT Station. Bus 65 is a trunk service that operates between Tampines and Harbourfront, passing through Bedok Reservoir, MacPherson Estate, and Central Singapore. Its overlap with the Downtown Line occurs from Tampines MRT Station to Bencoolen MRT Station. Bus 170 is a cross-border trunk service between Queen Street Terminal in Singapore and Larkin Terminal in Johor Bahru, passing through Rochor, Bukit Timah, and Woodlands. It has a complete overlap with the Downtown Line buffer from its origin at Queen Street to Bukit Panjang MRT Station.

Our results show that by encouraging commuters to shift to using newer MRT lines, specifically the Downtown Line in this case, can greatly benefit them in terms of substantial time savings. Even for bus stops that are not within the buffer, incorporating the use of the MRT into their travel routes results in a significant time improvement. In the case of Bus 65 for instance, using the Downtown Line for journeys to River Valley and Harbourfront results in time savings of up to 64 minutes. Even with Bencoolen MRT Station — the last stop that overlaps with the MRT buffer — as the origin, the time savings are significant. This makes the MRT a compelling alternative for travel along overlapping routes.

These findings indicate that removing or rerouting bus services with significant overlap with MRT lines can bring significant improvements to the public transport system. The time savings brought about can enhance commuter satisfaction, support MRT ridership growth, and potentially ease public concerns about changes to familiar bus routes.

Furthermore, our scoring framework provides a robust and interpretable foundation for making informed decisions on bus route adjustments. Each metric within the framework plays a distinct role; for instance, the overlap percentage directly measures route redundancy, allowing us to swiftly pinpoint routes with significant overlap that are prime candidates for removal or rerouting. This transparency in methodology ensures that decisions are based on quantifiable factors, enhancing interpretability for stakeholders and supporting a data-driven approach to transit planning.

In addition to the scoring framework, our further analysis of the top three bus routes highlights the most popular stops along each route. Identifying these high-traffic stops enables us to assess the potential impact of removing or rerouting these services on commuters. Specifically, we estimate the time savings passengers might gain by switching to MRT for these trips, providing a clearer picture of the benefits and trade-offs associated with each adjustment. 

From an operational perspective, reducing or adjusting redundant bus services translates into cost efficiencies. Eliminating or rerouting long trunk bus routes that mirror MRT lines reduces the need for duplicated resources, thereby lowering operational costs. These savings can then be reallocated to enhance service on other bus routes where demand is higher or access is limited, ultimately allowing transit operators to better meet the needs of commuters and provide more balanced coverage.

Such changes to public transport routes may affect certain groups more than others, particularly those in underserved or less accessible regions that rely heavily on bus services. Addressing this potential issue through community outreach and feedback can ensure that the changes do not disproportionately impact those without convenient MRT access. In addition, the cost savings that arise from adjusting the identified bus services can be utilised to provide more service to such areas. Acknowledging fairness as a priority will help to balance system efficiency with equitable access, promoting a transit network that serves all segments of the population.

Implementing these changes poses significant challenges, particularly given the potential impact on a large number of commuters. To mitigate disruption, a phased deployment approach — where route adjustments are introduced gradually and commuter responses are closely monitored at each stage — can be effective and flexible. This gradual rollout allows commuters time to familiarise themselves with alternative routes and adjust their routines, reducing the likelihood of sudden inconvenience. Moreover, by collecting and analysing feedback and travel patterns in real-time, this approach enables fine-tuning based on actual commuter behaviour. This ensures that the changes are both practical and responsive to commuter needs, ultimately increasing the overall effectiveness of the adjustments. Additionally, this incremental process generates valuable data for long-term transit planning, allowing for deeper insights into commuter preferences and facilitating more adaptive transit solutions.  

One potential concern with our model is the risk of reinforcing an over-reliance on MRT services, which could inadvertently diminish the flexibility of the overall public transport network. By prioritising bus routes with high MRT overlap for adjustment, the model may encourage a shift that makes MRT the sole transport option in these areas. While this may be efficient in the short term, it could reduce resilience in the event of MRT disruptions and limit transportation choices for commuters. Furthermore, the model’s reliance on quantitative metrics like passenger volume and overlap percentage, while informative, may exclude qualitative insights such as commuter satisfaction and convenience. This over-reliance on quantitative data could result in decisions that are technically optimal but may not align with the actual lived experiences and preferences of commuters.


### 4.3 Recommendations

Our recommendations for each of the three routes are as follows:
* **Bus 67:** We recommend a partial removal of the route, specifically the overlapping section after Bukit Panjang to Little India. Our analysis shows that taking the LRT from Choa Chu Kang to Bukit Panjang involves additional transfers and requires slightly more time. As a result, we recommend retaining the route to Bukit Panjang to provide a more direct and convenient option for commuters. Furthermore, given the high passenger demand for areas beyond the overlap — particularly on weekends for trips between Little India and Geylang, as well as between Little India and Tampines — removing only the redundant section allows us to retain valuable transit options for these high-demand segments. As a possible next step, further exploration of a potential reroute could be considered. 
For example, starting from Choa Chu Kang Interchange and extending through Tengah before reconnecting to the Downtown Line could help meet the needs of the developing Tengah area. This reroute would provide commuters with more direct access to the Downtown Line, supporting transit accessibility in this emerging planning area. However, this adjustment requires more in-depth analysis, which we could not explore due to time constraints. 
<br>
* **Bus 65:** Given the significant time savings achieved by using the Downtown Line to travel to destinations both within and beyond Bus 65’s overlap area with the MRT buffer, we recommend the removal of the entire route. We find that the time efficiency provided by the MRT in this corridor makes it redundant to keep the route in operation.
<br>
* **Bus 170:** As a cross-border service, Bus 170 is essential to the transit network. Removing the entire route would likely inconvenience many commuters who rely on this service. We therefore recommend a partial removal, covering the section from Queen Street to Bukit Panjang, where MRT coverage can efficiently replace the bus route. This compromise preserves the core functionality of Bus 170 for cross-border travel while minimising redundancy within the MRT buffer.


On top of our recommendations for these three services, we have broader suggestions in order to improve the effectiveness and equity of the findings in this project if it were to continue and be deployed.

In order to enhance the accuracy of our analysis and recommendations, improving upstream data quality would be highly beneficial. The current data limitations required us to make the simplifying assumptions mentioned earlier, such as the estimation of passenger demand at each bus stop. Addressing these limitations by capturing more granular data, such as stop-level passenger volumes for each bus service, would allow for a more refined analysis and produce more precise recommendations.

In addition, as our scoring framework relies heavily on quantitative metrics like passenger volume and overlap percentage, incorporating qualitative insights — such as feedback from commuter surveys or focus groups — would help provide a more holistic view of commuter needs. This approach would capture elements like commuter satisfaction and perceived convenience, allowing adjustments to be better aligned with actual commuter preferences and experiences.

In conclusion, our analysis provides actionable insights into optimising bus routes with high overlap along MRT lines, specifically recommending adjustments to Bus 67, 65, and 170. By encouraging a gradual transition to MRT alternatives where feasible, we aim to streamline operations and maximise resource allocation, ultimately enhancing Singapore’s public transport network. Moving forward, improving data quality and integrating additional datasets will enable even more precise and equitable adjustments, ensuring that our recommendations continue to support diverse commuter needs. Through a phased, data-driven deployment approach, we can implement these adjustments responsibly, fostering a flexible transit system that aligns with Singapore’s evolving urban landscape.

</div>