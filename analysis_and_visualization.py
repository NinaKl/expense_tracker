import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np

# Connect to your SQLite database
conn = sqlite3.connect('spendings.db')

### spendings   ###
query_2 = "SELECT * FROM grouped_transactions"
grouped_data = pd.read_sql_query(query_2, conn)


# Filter data for each currency
eur_data = grouped_data[grouped_data['Currency'] == 'EUR']
gbp_data = grouped_data[grouped_data['Currency'] == 'GBP']

# Plotting
for year in grouped_data['Year'].unique():
    year_data = grouped_data[grouped_data['Year'] == year]

    # Create a subplot for each year
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Set the background color of the figure
    fig.patch.set_facecolor('white')

    # Plot spendings for each month
    sns.barplot(x='Month', y=year_data['Amount'].abs(), hue='Currency', data=year_data[year_data['Type'] == 'Spendings'], ax=ax,errorbar=None)

    #ax.set_title(f'Expenses for Year {year}', fontsize=20)
    ax.set_xlabel('Month', fontsize=14)
    ax.set_ylabel('Amount', fontsize=14)
    ax.legend(title='Currency', fontsize=12)

    # Calculate total spendings and earnings for the year
    total_spendings_gbp = year_data[(year_data['Year'] == year) & (year_data['Type'] == 'Spendings') & (year_data['Currency'] == 'GBP')]['Amount'].abs().sum()
    total_spendings_eur = year_data[(year_data['Year'] == year) & (year_data['Type'] == 'Spendings') & (year_data['Currency'] == 'EUR')]['Amount'].abs().sum()
    total_earnings_gbp = year_data[(year_data['Year'] == year) & (year_data['Type'] == 'Earnings') & (year_data['Currency'] == 'GBP')]['Amount'].abs().sum()
    total_earnings_eur = year_data[(year_data['Year'] == year) & (year_data['Type'] == 'Earnings') & (year_data['Currency'] == 'EUR')]['Amount'].abs().sum()
    
    # Display total spendings on the plot with background color
    textbox = ax.text(0.5, 1.2, f'Expenses for Year {year}', fontsize=20, 
                      horizontalalignment='center', verticalalignment='top', 
                      transform=ax.transAxes)
    
    # Additional lines with different font sizes
    additional_text = (f'GBP Spendings: {total_spendings_gbp:.2f}, GBP Earnings: {total_earnings_gbp:.2f}, Total GBP: {(total_earnings_gbp - total_spendings_gbp):.2f}\n'
                       f'EUR Spendings: {total_spendings_eur:.2f}, EUR Earnings: {total_earnings_eur:.2f}, Total EUR: {(total_earnings_eur - total_spendings_eur):.2f}')
    ax.text(0.5, 1.1, additional_text, fontsize=12, 
            horizontalalignment='center', verticalalignment='top', 
            transform=ax.transAxes, multialignment='left',
            bbox=dict(boxstyle='round', facecolor='lightgrey', alpha=0.7))


    # Show the plot
    plt.tight_layout()
    plt.show()


#commit the changes & close the connection
#conn.close()