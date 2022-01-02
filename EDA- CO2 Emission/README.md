# Analysis on Factors Affecting Vehicular Emissions

I have considered the dataset of Co2 emission from kaggle. 

The question i have addressed in this analysis: 
what vehicle mechanical demographic variables are most correlated with an increase in CO2 emissions?
 
I also had a few secondary questions I wanted to answer:

•	if low end priced cars and high-end premium cars got a variation towards  fuel consumption, 

•	if CVTs are more or less likely to be found on larger engines

In my EDA, I concluded that the most significant factors in increasing a vehicle’s emissions are its variant, engine, and fuel consumption. Cylinder number goes hand-in-hand with displacement, so that is included as well. What surprised me was that transmission and fuel types did not affect emissions as much as said variables. Based on this, I would recommend purchasing a compact, midsize sedan, or station wagon, equipped with a 4-cylinder engine running regular gasoline, to reduce emissions. Such cars are usually very inexpensive, so it’s a win-win situation! 

I then plotted a PMF of the fuel consumption of gas and premium gas cars. There was indeed a difference between premium Vehicles had higher fuel consumption vehicles; it made me to to run the hypothesis test to test the difference in means, and the output yielded a p-value significantly smaller than zero, confirming that regular gasoline does, in fact, consume less fuel. It is also much less expensive, so the only reason one should purchase premium gas is if their car requires it.

The  box plot of emissions vs car manufacturer. I found that (no surprise) all sports car and most luxury car brands are guilty of emitting more CO2 than other cars. Based on the plot, the following brands have the lowest emissions and are the brands I would recommend purchasing: Fiat, Honda, Hyundai, Mazda, Mini, Smart, and Volkswagen. If one is adamant on buying a luxury car, they should consider Audi or Acura; these brands are in the middle of the emissions spectrum.

After calculating the percentage of CVT transmissions found for all cars with a certain number of cylinders and plotted this against the number of cylinders. The observation I made here is occurrence of CVTs dropped with increasing engine size. Agreed, as CVTs are already very expensive and have issues with higher loads.
