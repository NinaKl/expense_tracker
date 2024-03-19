import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np

### CREATE FAKE DATA FOR DEMONSTRATION ###

data_size = 1000
data = {
    'Year': np.random.choice([2018,2019,2020, 2021, 2022, 2023], size=data_size),
    'Month': pd.to_datetime(np.random.choice(pd.date_range('2018-01-01', '2023-12-31', freq='M'), size=data_size)).to_period('M'),
    'Type': np.random.choice(['Earnings', 'Spendings'], size=data_size),
    'Currency': np.random.choice(['EUR', 'GBP'], size=data_size),
    'Amount': np.random.normal(loc=0, scale=100, size=data_size)  # Generate random amounts
}

# Ensure Spendings have negative amounts
data['Amount'] = np.where(data['Type'] == 'Spendings', -np.abs(data['Amount']), data['Amount'])

# Create DataFrame
data_2 = pd.DataFrame(data)

# Convert 'Year' column to string (for an easier compatibility)
data_2['Year'] = data_2['Year'].astype(str)

# Convert 'Month' column to datetime
data_2['Month'] = pd.to_datetime(data_2['Month'].astype(str), format='%Y-%m')

# Extract year and month separately
data_2['Year'] = data_2['Month'].dt.year
data_2['Month'] = data_2['Month'].dt.month

# Group data by year, month, type, and currency, and sum the amounts for each group
grouped_data = data_2.groupby(['Year', 'Month', 'Type', 'Currency'])['Amount'].sum().reset_index()

####               ####
#### end fake data #### 

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
    
    # Adjust subplot parameters to leave space for axis labels and title
    plt.subplots_adjust(left=0.1, bottom=0.1, right=0.95, top=0.84, wspace=0.2, hspace=0.2)

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