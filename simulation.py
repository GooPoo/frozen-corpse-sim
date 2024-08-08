import requests
import random

from corpse_data import product_items, umber_corpse, tungsten_corpse, vanguard_corpse, perfect_to_flawless

def main():
    url = "https://api.hypixel.net/v2/skyblock/bazaar"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        
        bazaardict = {}
        missing_items = set(product_items)
        
        for product_id, product_info in data.get("products", {}).items():
            if product_id in product_items:
                quick_status = product_info.get("quick_status")
                if quick_status:
                    sell_price = quick_status.get("sellPrice")
                    buy_price = quick_status.get("buyPrice")
                    bazaardict[product_id] = {
                        "sellPrice": sell_price,
                        "buyPrice": buy_price
                    }
                    missing_items.discard(product_id)
        
        # Adjust PERFECT items (Idea is you take the profit of the crystal, instead of the Perfect gem)
        for perfect_item, flawless_item in perfect_to_flawless.items():
            if perfect_item in bazaardict and flawless_item in bazaardict:
                flawless_sell_price = bazaardict[flawless_item].get("sellPrice", 0)
                flawless_buy_price = bazaardict[flawless_item].get("buyPrice", 0)
                
                bazaardict[perfect_item]["sellPrice"] -= 5 * flawless_sell_price
                bazaardict[perfect_item]["buyPrice"] -= 5 * flawless_buy_price

        if missing_items:
            print("\nMissing in request:")
            for item in missing_items:
                print(item)
                print("\n")

        print("========================================")
        print_bazaardict_sorted_by_sell_price(bazaardict)
        print("========================================")

        # Simulation parameters
        num_simulations = 10000

        # Simulate for Tungsten corpse
        simulate_corpse(tungsten_corpse, bazaardict, num_simulations, min_rolls=4, max_rolls=7, key="TUNGSTEN_KEY")

        # Simulate for Umber corpse
        simulate_corpse(umber_corpse, bazaardict, num_simulations, min_rolls=4, max_rolls=7, key="UMBER_KEY")

        # Simulate for Vanguard corpse
        simulate_corpse(vanguard_corpse, bazaardict, num_simulations, min_rolls=5, max_rolls=8, key="SKELETON_KEY")
    

    else:
        print(f"Error: {response.status_code}")

def print_bazaardict_sorted_by_sell_price(bazaardict):
    items_with_prices = [(item, details.get("sellPrice", 0)) for item, details in bazaardict.items()]
    
    sorted_items = sorted(items_with_prices, key=lambda x: x[1], reverse=True)
    
    print("Items sorted by sell price:")
    for item, sell_price in sorted_items:
        formatted_sell_price = "{:,.2f}".format(sell_price)
        print(f"{item}: ${formatted_sell_price}")

def weighted_choice(loot_table):
    items = list(loot_table.keys())
    weights = [loot_table[item] for item in items]  # Make sure weights are integers
    total_weight = sum(weights)
    rand = random.uniform(0, total_weight)
    cumulative_weight = 0
    for item, weight in zip(items, weights):
        cumulative_weight += weight
        if rand < cumulative_weight:
            return item


def prepare_loot_table(corpse_dict):
    loot_table = {}
    for item, details in corpse_dict.items():
        if isinstance(details, list):
            # Sum up weights for the item
            total_weight = sum(entry['weight'] for entry in details)
            loot_table[item] = total_weight
        else:
            loot_table[item] = details['weight']
    
    return loot_table


def simulate_rolls(corpse_dict, bazaardict, min_rolls, max_rolls, key):
    results = {}
    loot_table = prepare_loot_table(corpse_dict)
    
    total_rolls = random.randint(min_rolls, max_rolls)

    # 20% chance to add an extra roll
    if random.random() < 0.2:
        total_rolls += 1

    total_profit = 0
    
    for _ in range(total_rolls):
        chosen_item = weighted_choice(loot_table)
        
        if isinstance(corpse_dict[chosen_item], list):
            amounts_weights = {entry['amount']: entry['weight'] for entry in corpse_dict[chosen_item]}
            amount = weighted_choice(amounts_weights)
        else:
            amount = corpse_dict[chosen_item]['amount']
        
        if chosen_item not in results:
            results[chosen_item] = 0
        results[chosen_item] += amount

        if chosen_item in bazaardict:
            sell_price = bazaardict[chosen_item].get("sellPrice", 0) # Change sellPrice to buyPrice if you want to Sell Order instead of insta-sell
            total_profit += amount * sell_price

    key_price = bazaardict[key].get("sellPrice", 0) # Key Price based on Buy Order
    total_profit = total_profit - key_price
    
    return results, total_profit

def simulate_corpse(corpse_dict, bazaardict, num_simulations, min_rolls, max_rolls, key):

    loot_table = prepare_loot_table(corpse_dict)

    total_results = {}
    total_profit = 0

    for _ in range(num_simulations):
        results, profit = simulate_rolls(corpse_dict, bazaardict, min_rolls, max_rolls, key)
        total_profit += profit
        for item, amount in results.items():
            if item not in total_results:
                total_results[item] = 0
            total_results[item] += amount

    sorted_results = []
    for item, amount in total_results.items():
        sell_price = bazaardict.get(item, {}).get("sellPrice", 0) # Change sellPrice to buyPrice if you want to Sell Order instead of insta-sell
        total_sell_cost = amount * sell_price
        sorted_results.append((item, amount, total_sell_cost))
    
    sorted_results.sort(key=lambda x: x[2], reverse=True)

    average_profit = total_profit / num_simulations
    formatted_profit = "{:,.2f}".format(total_profit)
    formatted_average_profit = "{:,.2f}".format(average_profit)
    print("Number of Simulations: " + str(num_simulations))
    print("Total Results:")
    for item, amount, total_sell_cost in sorted_results:
        formatted_total_sell_cost = "{:,.2f}".format(total_sell_cost)
        print(f"{item}: {amount} (${formatted_total_sell_cost})")
    print(f"Total Profit: ${formatted_profit}")
    print(f"Average Profit: ${formatted_average_profit}")
    print("========================================")


if __name__ == "__main__":
    main()