# README

To run the code : 
- Use Python 3.10.9
- Install the requirements.txt
- Execute the code

# Here quick ideas for data analysis


```python
import pandas as pd
from Scrape_huffnpuffer import *
```


```python
data = pd.read_csv("product_huff_puffer.csv",sep=';')
data.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>product</th>
      <th>options</th>
      <th>average_score</th>
      <th>recommand</th>
      <th>specifications</th>
      <th>package_content</th>
      <th>ingredients</th>
      <th>nb_review</th>
      <th>scores_distribution</th>
      <th>caracteristics_scores</th>
      <th>reviews</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>candy-king-air-disposable-vape</td>
      <td>[{'option': 'BlueRazz Straws', 'price': 14.99}...</td>
      <td>4.4</td>
      <td>87.0</td>
      <td>['11.0 mL per e-cigarette', '5% nicotine by we...</td>
      <td>['1 X\xa0Candy King Air Disposable E-Cigarette']</td>
      <td>['• USP Grade Propylene Glycol (60%)', '• USP ...</td>
      <td>128</td>
      <td>{5: 84, 4: 27, 3: 9, 2: 5, 1: 3}</td>
      <td>{'flavor': 86.28048780487805, 'sweetness': 78....</td>
      <td>['Worked great', 'Great taste', 'I liked this ...</td>
    </tr>
    <tr>
      <th>1</th>
      <td>daze-egge-disposable-vape</td>
      <td>[{'option': '7obacco', 'price': 11.99}, {'opti...</td>
      <td>4.7</td>
      <td>90.0</td>
      <td>['7.0 mL per e-cigarette', '5% nicotine by wei...</td>
      <td>['1 X\xa0Daze Egge Disposable E-Cigarette']</td>
      <td>['• Propylene Glycol (PG)', '• Vegetable Glyce...</td>
      <td>174</td>
      <td>{5: 136, 4: 21, 3: 14, 2: 3, 1: 0}</td>
      <td>{'flavor': 87.20930232558139, 'sweetness': 74....</td>
      <td>['This flavor tastes wonderful! Like a vanilla...</td>
    </tr>
    <tr>
      <th>2</th>
      <td>daze-ohmlet-disposable-vape</td>
      <td>[{'option': 'Blueberry Cake', 'price': 15.99},...</td>
      <td>4.6</td>
      <td>89.0</td>
      <td>['15.0 mL per e-cigarette', '5% nicotine by we...</td>
      <td>['1 X\xa0Daze Ohmlet Disposable\xa0E-Cig']</td>
      <td>['• Propylene Glycol (PG)', '• Vegetable Glyce...</td>
      <td>244</td>
      <td>{5: 186, 4: 30, 3: 17, 2: 6, 1: 5}</td>
      <td>{'flavor': 88.72832369942196, 'sweetness': 78....</td>
      <td>['This is my go to disposable. Reason being th...</td>
    </tr>
    <tr>
      <th>3</th>
      <td>elfbar-airo-max-disposable-vape</td>
      <td>[{'option': 'Banana Pineapple', 'price': 14.99...</td>
      <td>4.7</td>
      <td>93.0</td>
      <td>['13.0 mL of e-liquid per e-cigarette', 'Appro...</td>
      <td>['1 X\xa0Elf Bar Airo Max Disposable E-Cigaret...</td>
      <td>['• Vegetable Glycerin (VG)', '• Propylene Gly...</td>
      <td>85</td>
      <td>{5: 65, 4: 14, 3: 4, 2: 1, 1: 1}</td>
      <td>{'flavor': 89.99999999999999, 'sweetness': 82....</td>
      <td>['Good taste. Last long time. Have only tried ...</td>
    </tr>
    <tr>
      <th>4</th>
      <td>elf-bar-bc5000-disposable-vape</td>
      <td>[{'option': 'Beach Day', 'price': 14.99}, {'op...</td>
      <td>4.9</td>
      <td>97.0</td>
      <td>['13.0 mL per e-cigarette', '5% nicotine by we...</td>
      <td>['1 X\xa0Elf Bar BC5000 Disposable E-Cig']</td>
      <td>['• Vegetable Glycerin (VG)', '• Propylene Gly...</td>
      <td>939</td>
      <td>{5: 841, 4: 71, 3: 17, 2: 5, 1: 5}</td>
      <td>{'flavor': 94.39252336448598, 'sweetness': 84....</td>
      <td>['It was tasty.', 'I like it', 'Best flavor', ...</td>
    </tr>
  </tbody>
</table>
</div>




```python
data.loc[:, data.columns != 'product'] = str_to_structured(data.drop(['product'],axis=1))
```

We can see the word "flavor" being extremely used in the reviews. It seem's to be the most important caracteristics as we will see


```python
data['most_commun_words'] = data[data['nb_review']>0]["reviews"].apply(lambda x : most_commun_words(x,5))
```


```python
show_most_commun_words(data[data['nb_review']>0]['most_commun_words'])
```


    
![png](README_analyse_files/README_analyse_8_0.png)
    


Looking at the best caracteristic score we see that flavor come hugely in front of the others. It seems people are mostly interested in the flavor and that's what huff and puffer seems to target. 


```python
data['best_caracteristic'] = data[data['nb_review']>0]["caracteristics_scores"].apply(best_caracteristic)
```


```python
show_best_caracteristic(data[data['nb_review']>0]['best_caracteristic'])
```


    
![png](README_analyse_files/README_analyse_11_0.png)
    


As we see product with a better flavor than the to other caracteristic tends to have a better overall note.


```python
avg_note_carac = note_by_best_caracteristic(data[data['nb_review']>0])
print(f"Average note with flavor as best caracteristic : {avg_note_carac['flavor']}.")
print(f"Average note with long_lasting as best caracteristic : {avg_note_carac['long_lasting']}.")
print(f"Average note with sweetness as best caracteristic : {avg_note_carac['sweetness']}.")
```

    Average note with flavor as best caracteristic : 4.632258064516128.
    Average note with long_lasting as best caracteristic : 4.433333333333334.
    Average note with sweetness as best caracteristic : 4.2.
    

As we can see in the next plot, note and flavor seems correlated


```python
show_note_by_caracteristic(data[data['nb_review']>0],'flavor')
```


    
![png](README_analyse_files/README_analyse_15_0.png)
    


But are notes really related to what people thinks ?


```python
data['sentiment'] = data[data['nb_review']>0]['reviews'].apply(polarity_review)
```

To have an idea od the scale :


```python
print(f"With the word Love we get a score of : {TextBlob('Love').sentiment.polarity}")
print(f"With the word Hate we get a score of : {TextBlob('Hate').sentiment.polarity}")
```

    With the word Love we get a score of : 0.5
    With the word Hate we get a score of : -0.8
    

We can see globaly notes are hight where sentiments polarity are too. But we can see by the distribution people who gives reviews tends to be a little bit more generous in note than in comments.


```python
Note_by_sentiment = data[data['nb_review']>0][['average_score','sentiment']].sort_values(0,axis=1)

# Set the size of the figure
fig, ax = plt.subplots(figsize=(10, 8))

# Create a bar chart of the summed count of each word
ax.scatter(Note_by_sentiment['sentiment'],Note_by_sentiment['average_score'])
ax.set_xlabel('Sentiment')
ax.set_ylabel('Average article note')
ax.set_title(f'Article note by sentiment score')
plt.show()
```


    
![png](README_analyse_files/README_analyse_21_0.png)
    


This scrapping code and analysis can be upgrad with a more precise idea of what we want from this site and time (ingredients aren't maybe relevant information, scrape more deeply the reviews (scrape not only texts but everything),...). 
