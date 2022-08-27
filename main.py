# File name: main.py

from kivy.lang import Builder
from kivymd.app import MDApp

from kivy.storage.jsonstore import JsonStore
import json
import os
from datetime import date


class EarningCalcApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.accent_palette = "LightBlue"
        self.theme_cls.material_style = "M3"

        return Builder.load_file("ec.kv")

    current_date = date.today()
    now = current_date.strftime("%Y-%m-%d")

    # Clears user input and replaces it with default hint-text
    def clear_settings(self):
        self.root.ids.name_input.text = ""
        self.root.ids.email_input.text = ""
        self.root.ids.sales_tax_input.text = ""
        self.root.ids.shop_percent_input.text = ""

    # Clear start/end date fields used to generate reports
    def clear_dates(self):
        self.root.ids._start_date.text = ""
        self.root.ids._end_date.text = ""

    # Create set of variables for storing data in json format using JsonStore
    user_info = JsonStore("ec_settings/user_settings.json")
    expenses_data = JsonStore(f"ec_expenses/{now}.expense_data.json")
    sale_info = JsonStore(f"ec_sales/{now}.sale_info.json")
    earning_reports = JsonStore(f"ec_reports/{now}.json")

    # Generate an Earning Report for specified date-range
    def generate_report(self):
        start_date = self.root.ids._start_date.text
        end_date = self.root.ids._end_date.text
        # From user input slice string to access just days specified
        d_start = start_date[8:]
        d_end = end_date[8:]
        # Create path variables for directories to be accessed
        path = "./ec_expenses"
        path1 = "./ec_sales"
        # Create lists of file names for expense files and sales files
        files_exp = [f for f in os.listdir(path)]
        files_sale = [f for f in os.listdir(path1)]
        # Create list of expense files that are within specified date range
        exp_in_range = [
            file for file in files_exp if file[8:10] >= d_start and file[8:10] <= d_end
        ]
        # Create list of sales files that are within specified date range
        sales_in_range = [
            file for file in files_sale if file[8:10] >= d_start and file[8:10] <= d_end
        ]
        # Create empty lists for storing data temporarily
        exp_cost = []
        exp_name = []
        sale_name = []
        sale_est_tax = []
        sale_amt_charged = []
        sale_amt_for_shop = []
        sale_deposit = []

        # Access data from expense files
        for i in exp_in_range:
            with open(f"ec_expenses/{i}", "r") as file:
                fileData = json.load(file)
                for k in fileData.keys():
                    exp = float(fileData[k]["cost"])
                    exp_name.append(k)
                    exp_cost.append(exp)
        # Access data from sales files
        for i in sales_in_range:
            with open(f"ec_sales/{i}", "r") as file:
                saleData = json.load(file)
                for k in saleData.keys():
                    sale_name.append(k)
                    amt_charged = float(saleData[k]["sale"])
                    sale_amt_charged.append(amt_charged)
                    est_tax = float(saleData[k]["est_sales_tax"])
                    sale_est_tax.append(est_tax)
                    amt_owed_shop = float(saleData[k]["shop_owed"])
                    sale_amt_for_shop.append(amt_owed_shop)
                    deposit = float(saleData[k]["deposit"])
                    sale_deposit.append(deposit)
        total_sales = float(sum(sale_amt_charged))
        total_est_tax = float(sum(sale_est_tax))
        total_exp = float(sum(exp_cost))
        total_deposits = float(sum(sale_deposit))
        total_owed_shop = float(sum(sale_amt_for_shop))
        total_est_earnings = (total_sales + total_deposits) - (
            total_est_tax + total_exp + total_owed_shop
        )
        # Create a json file storing key data from report
        self.earning_reports.put(
            "Earning Report",
            total_sales=f"${total_sales:.2f}",
            total_estimated_tax=f"${total_est_tax:.2f}",
            total_expenses=f"${total_exp:.2f}",
            total_shop_cut=f"${total_owed_shop:.2f}",
            total_deposit_amt=f"${total_deposits:.2f}",
        )
        # Create a text file format to access for earning report
        current_date = date.today()
        now = current_date.strftime("%Y-%m-%d")
        ec_report_file = f"ec_reports/{now}.txt"
        with open(ec_report_file, "w") as file_object:
            file_object.write(
                f"Earning Report for {start_date} - {end_date}:\n\tCreated on {now}\n\n\tTotal Sales: ${total_sales:.2f}\n\tTotal Deposits Amount: ${total_deposits:.2f}\n\tTotal Estimated Sales Tax Owed: ${total_est_tax:.2f}\n\tTotal Cost of Expenses Purchased: ${total_exp:.2f}\n\tTotal Amount Owed to Shop: ${total_owed_shop:.2f}\n\tTotal Estimated Earnings: ${total_est_earnings:.2f}"
            )

    # Save user info from settings
    def save_user_info(self):
        self.user_info.put(
            "user_settings",
            name=self.root.ids.name_input.text,
            user_email=self.root.ids.email_input.text,
            sales_tax=self.root.ids.sales_tax_input.text,
            shop_percent=self.root.ids.shop_percent_input.text,
        )

    def exp_save(self):
        new_exp = self.root.ids.exp_name.text
        cost = float(self.root.ids.exp_cost.text)
        quantity_per = float(self.root.ids.exp_quantity.text)
        unit_cost = cost / quantity_per
        self.expenses_data.put(
            f"{new_exp}",
            cost=f"{cost:.2f}",
            quantity=f"{quantity_per}",
            cost_per=f"{unit_cost:.2f}",
        )
        self.root.ids.exp_name.text = ""
        self.root.ids.exp_quantity.text = ""
        self.root.ids.exp_cost.text = ""

    def sale_info_save(self):
        customer_name = self.root.ids.sale_name.text
        sale_amount = float(self.root.ids.amt_charged.text)
        deposit_amount = float(self.root.ids.amt_deposit.text)
        total_sale = sale_amount + deposit_amount
        with open("ec_settings/user_settings.json", "r") as file:
            userData = json.load(file)
        sales_tax = float(userData["user_settings"]["sales_tax"])
        shop_cut = float(userData["user_settings"]["shop_percent"])
        shop_owed = sale_amount * shop_cut
        est_tax = (sale_amount - shop_owed) * sales_tax
        est_earnings = total_sale - (shop_owed + est_tax)
        self.sale_info.put(
            f"{customer_name}",
            sale=f"{sale_amount:.2f}",
            deposit=f"{deposit_amount:.2f}",
            total=f"{total_sale:.2f}",
            shop_owed=f"{shop_owed:.2f}",
            est_sales_tax=f"{est_tax:.2f}",
            est_earnings=f"{est_earnings:.2f}",
        )
        self.root.ids.sale_name.text = ""
        self.root.ids.amt_charged.text = ""
        self.root.ids.amt_deposit.text = ""


if __name__ == "__main__":
    EarningCalcApp().run()
