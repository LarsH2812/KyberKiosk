import datetime
import math
import numpy as np
import sys
import time

from PySide6.QtGui import QKeySequence, QShortcut, QPainter, QColor, QFont
from PySide6.QtWidgets import QApplication, QMainWindow, QDialog, QTableWidgetItem, QHBoxLayout
from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlRecord, QSqlTableModel
from PySide6.QtCore import Qt, QPoint
from PySide6.QtCharts import QBarCategoryAxis,QBarSeries,QBarSet,QChart,QChartView,QLineSeries,QValueAxis,QAbstractBarSeries

from ui_main import Ui_MainWindow
import sqlite3


KKdb = sqlite3.connect("KyberKiosk.sqlite")
cur = KKdb.cursor()

starttime = time.time()
stoptime = time.time()

currentUser = {
    'ID':0,
    'name':"naam",
    'title':"lid",
    'amount':0.0,
    'password':"ps",
    'block':False,
    'qr':"12321"
}

class MainWindow:
    def __init__(self):
        self.main_win = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.main_win)

        # set start conditions for the application
        self.ui.stackedWidget.setCurrentWidget(self.ui.login)
        self.ui.pages.setCurrentWidget(self.ui.buy_page)
        self.ui.Users.setCurrentWidget(self.ui.UserMenu_page)
        self.ui.line_qr.setFocus()
        self.ui.buy_btn.setChecked(True)

        # initialize all connections, needed for a functional loginscreen
        self.ui.logout_btn.clicked.connect(self.logout)
        self.ui.btn_login.clicked.connect(self.login)
        self.ui.btn_qr.clicked.connect(self.filqrlogin)
        self.ui.line_qr.returnPressed.connect(self.qrlogin)
        self.ui.line_stdnr.returnPressed.connect(self.ui.line_pswrd.setFocus)
        self.ui.line_pswrd.returnPressed.connect(self.ui.btn_login.click)
        self.ui.btn_retpass.clicked.connect(self.retrivePass)

        # initialize all connection, needed for a functional password retreval
        self.ui.line_stdnr_ret.returnPressed.connect(self.ui.btn_next.click)
        self.ui.line_qr_ret.returnPressed.connect(self.ui.btn_next.click)
        self.ui.btn_next.clicked.connect(self.verifyID)
        self.ui.btn_save.clicked.connect(self.changePass)

        #initialize the menu buttons to redirect to the correct window 
        self.ui.buy_btn.clicked.connect(self.toBuy)
        self.ui.stat_btn.clicked.connect(self.toStat)
        self.ui.prof_btn.clicked.connect(self.toProf)
        self.ui.prod_btn.clicked.connect(self.toProd)
        self.ui.user_btn.clicked.connect(self.toUser)

        #initialize everything needed for the buy screen
        self.ui.cart_fld.verticalHeader().setHidden(True)
        self.ui.cart_fld.setColumnHidden(0,True)
        self.ui.cart_fld.setColumnWidth (1, 810)
        self.ui.cart_fld.setColumnWidth (2, 150)
        self.ui.cart_fld.setColumnWidth (3, 150)
        self.ui.cart_fld.setColumnWidth (4, 150)
        self.ui.item_fld.returnPressed.connect(self.getItem)
        self.ui.pay_btn.clicked.connect(self.pay)        

        #initialize everythin neeeded for the product screen
        self.ui.ProdList.verticalHeader().setHidden(True)
        self.ui.ProdList.setColumnWidth(0, 200)
        self.ui.ProdList.setColumnWidth(1, 570)
        self.ui.ProdList.setColumnWidth(2, 100)
        self.ui.ProdList.setColumnWidth(3, 125)
        self.ui.ProdList.setColumnWidth(4, 125)
        self.ui.ProdList.setColumnWidth(5, 140)
        self.ui.ProdList.setColumnHidden(6, True)
        self.ui.NewProd_btn.clicked.connect(self.addProd)
        self.ui.EditProd_btn.clicked.connect(self.updateProducts)

        #initialize everything needed for the Users screen
        self.ui.EditUser_btn.clicked.connect(self.toEditUser)
        self.ui.NewUser_btn.clicked.connect(self.toNewUser)
        self.ui.UpdateUser_btn.clicked.connect(self.toUpdateUser)

        self.ui.line_ID.returnPressed.connect(self.getUserInfo)
        self.ui.btn_EDIT.clicked.connect(self.updateUserInfo)
        self.ui.btn_ADD.clicked.connect(self.addUser)

        self.ui.INC_line_ID.returnPressed.connect(self.getUserAmount)
        self.ui.INC_line_INC.textEdited.connect(self.increaseAmount)
        self.ui.INC_line_INC.returnPressed.connect(self.ui.btn_INC.click)
        self.ui.btn_INC.clicked.connect(self.saveNewAmount)

        #initialize everything needed for a functional statistics screen


        self.chart = QChart()
        # self.chart.setTitle("Top 5 aankopen")
        self.chart.setTitleFont(QFont("Segoe UI",22))
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.legend().setVisible(False)
        self.chart.setBackgroundVisible(False)
        self.chart.setPlotAreaBackgroundVisible(False)

        self.view = QChartView(self.chart)
        self.view.setRenderHint(QPainter.Antialiasing)
        
        self.view.setStyleSheet("""
            background-color: #1f1f1f;
            font-size: 22px;
        """)
        self.statlayout = QHBoxLayout()
        self.statlayout.addWidget(self.view)
        self.ui.stat_widget.setLayout(self.statlayout)

        

        #Initialize the shortcut for quick return to previous window/quick logout
        escShortcut = QShortcut(self.ui.centralwidget)
        escShortcut.setKey('Escape')
        escShortcut.activated.connect(self.escShortcut)
        #initialize the shortcut for to enable the deletion of a row in the table
        delItemShortcut = QShortcut(self.ui.centralwidget)
        delItemShortcut.setKey('ctrl+Delete')
        delItemShortcut.activated.connect(self.deleteRow)

    def escShortcut(self):
        if self.ui.stackedWidget.currentIndex() == 0:
            sys.exit()
        elif self.ui.pages.currentWidget() == self.ui.buy_page:
            if self.ui.cart_fld.rowCount() == 0:
                self.logout()
        elif self.ui.pages.currentWidget() == self.ui.user_page:
            if self.ui.Users.currentWidget() in (self.ui.NewUser_page, self.ui.EditUser_page, self.ui.UpdateUser_page):
                self.ui.Users.setCurrentIndex(0)
            else:
                self.ui.pages.setCurrentIndex(0)
                self.ui.buy_btn.setChecked(True)
        else:
            self.ui.pages.setCurrentWidget(self.ui.buy_page)
            self.ui.buy_btn.setChecked(True)
            
    def show(self):
        self.main_win.show()
        self.main_win.showFullScreen()

    #function that sends a query to the connected db and, checks if the filled in credentials are correct. If not, it gives adequate responce about the error.
    def login(self):
        global starttime
        self.resetInfoLines()
        user = self.ui.line_stdnr.text()
        password = self.ui.line_pswrd.text()

        if user != '':
            query = f'SELECT * FROM  Users WHERE ID = \'{user}\''
            cur.execute(query)
            result = cur.fetchone()
            if result != None:
                if password == result[4]:
                    self.ui.stackedWidget.setCurrentIndex(1)
                    self.toBuy()
                    starttime = time.time()
                    self.getCurrentUserInfo(result)
                    self.ui.line_stdnr.clear()
                    self.ui.line_pswrd.clear()
                else:
                    self.ui.line_pswrd.clear()
                    self.ui.ERROR_PSWRD.setText('[INFO] Verkeerd Wachtwoord')
            else:
                self.ui.line_stdnr.clear()
                self.ui.line_pswrd.clear()
                self.ui.line_stdnr.setFocus()
                self.ui.ERROR_STDNR.setText('[INFO] Student Onbekend')
        else:
            self.ui.line_stdnr.setFocus()
            self.ui.ERROR_PSWRD.setText('[INFO] Geen Student nummer opgegeven')

    #the code for loggin out, which resets the current ui, and all querries
    def logout(self):
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.pages.setCurrentWidget(self.ui.buy_page)
        self.ui.buy_btn.setChecked(True)
        self.ui.line_qr.setFocus()
        self.ui.line_stdnr.clear()
        self.ui.line_pswrd.clear()
        self.ui.line_qr.clear()
        self.clearTable(self.ui.cart_fld)
        self.ui.ERROR_ITMFLD.clear()
    #this fuction enables the use of qr codes, so that when a qr code is scanned, the output can be used.
    def filqrlogin(self):
        self.ui.line_qr.clear()
        self.resetInfoLines()
        self.ui.line_qr.setFocus()
    #this function checks the scanned qr code against the qr-codes in the database.
    def qrlogin(self):
        global starttime
        qr = self.ui.line_qr.text()
        query = f"SELECT * FROM Users WHERE qrCodes = \'{qr}\'"
        cur.execute(query)
        result = cur.fetchone()
        if result != None:
            currentUser['ID'] : str(result[0])
            self.getCurrentUserInfo(result)
            self.ui.stackedWidget.setCurrentIndex(1)
            self.toBuy()
            starttime = time.time()
        else:
            self.ui.ERROR_QRFLD.setText('[INFO] qr Onbekend')
            self.ui.line_qr.setFocus()
            self.ui.line_qr.clear()
        
    def retrivePass(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.retPSWRD)
        self.ui.retsteps.setCurrentIndex(0)
        self.ui.line_qr_ret.clear()
        self.ui.line_stdnr_ret.clear()
        self.ui.line_pass_ret.clear()
        self.ui.line_stdnr_ret.setFocus()
    
    def verifyID(self):
        if self.ui.line_qr_ret.text() == "":
            self.ui.line_qr_ret.clear()
            self.ui.line_qr_ret.setFocus()
        else:
            userid = self.ui.line_stdnr_ret.text()
            userqr = self.ui.line_qr_ret.text()
            query = f"SELECT qrCodes FROM Users WHERE ID = \'{userid}\'"
            cur.execute(query)
            result = cur.fetchone()
            if result == None:
                self.ui.ERROR_VERIFY.setText("[INFO] Er is geen account in het systeem met dit studentnummer.\n\tVraag het huidig bestuur om hulp.")

            elif result[0] == userqr:
                self.ui.ERROR_VERIFY.clear()
                self.ui.retsteps.setCurrentIndex(1)
            else:
                self.ui.ERROR_VERIFY.setText("[INFO] De qr-code komt niet overeen met wat er geregistreerd staat.\n\tVraag het huidig bestuur om hulp.")
                self.ui.line_qr_ret.clear()
    def changePass(self):
        userid = self.ui.line_stdnr_ret.text()
        userPass = self.ui.line_pass_ret.text()
        query = f"  UPDATE Users SET password = \'{userPass}\' WHERE ID = \'{userid}\'"

        try:
            cur.execute(query)
            KKdb.commit()
        except:
            self.ui.ERROR_PSWRD.setText("[ERROR] Het is niet gelukt om je wachtwoord aan te passen,\nvraag help van iemand van het huidig bestuur")
        else:
            self.ui.ERROR_PSWRD.setText("[INFO] Wachtwoord succesvol geüpdate")
        finally:
            self.ui.stackedWidget.setCurrentIndex(0)
            self.ui.line_stdnr_ret.clear()
            self.ui.line_pass_ret.clear()
            self.ui.line_qr_ret.clear()
            self.ui.line_stdnr.setFocus()
            
   #the following functions handle the transfer to the different pages
    def toBuy(self):
        self.ui.pages.setCurrentWidget(self.ui.buy_page)
        self.ui.item_fld.setFocus()
        query = f"SELECT Amount FROM Users WHERE ID = '{currentUser['ID']}'"
        cur.execute(query)
        res = cur.fetchone()[0]
        self.ui.teGoed_fld.setText(format(res,'.2f'))


    def toStat(self): 
        self.chart.removeAllSeries()
        self.ui.pages.setCurrentWidget(self.ui.stat_page)
        query = f"SELECT * FROM History WHERE ID = '{currentUser['ID']}'"
        cur.execute(query)
        res = np.array(cur.fetchall())

        # print(res)
        prodCount = {}
        total_spend = 0
        total_bought = 0
        for i in range(len(res)):
            prodID = str(res[i][4])
            print(res)
            if prodID not in prodCount:
                prodCount[prodID] = int(res[i][2])
            else:
                prodCount[prodID] = prodCount[prodID] + int(res[i][2])
            total_spend = total_spend + float(res[i][5])
            total_bought = total_bought + int(res[i][2])
        sorteddict = dict(sorted(prodCount.items(), key=lambda item: item[1], reverse = True))

        keys = list(sorteddict.keys())
        values = list(sorteddict.values())

        self.series = QBarSeries()

        self.set = QBarSet('Top 5')
        self.set.append(values)
        self.set.setBorderColor(QColor.fromRgb(255,255,255,0))
        self.set.setColor(QColor.fromRgb(0x6b,0x1f,0xe8))
        self.set.setLabelFont(QFont("Segoe UI",22))
        self.series.append(self.set)

        self.series.setLabelsVisible(True)
        self.series.setLabelsPosition(QAbstractBarSeries.LabelsInsideBase)
        self.chart.addSeries(self.series)
        
        self.bars = keys
        self.axis_x = QBarCategoryAxis()
        self.axis_x.setCategories(self.bars)
        try:
            self.chart.removeAxis(self.chart.axes()[0])
        except:
            pass
        finally:
            self.chart.setAxisX(self.axis_x,self.series)

        self.chart.axes()[0].setLabelsColor(QColor.fromRgb(255,255,255))
        self.chart.axes()[0].setLabelsFont(QFont("Segoe UI",22))
        
        self.ui.fld_spend.setText(format(total_spend,'.2f'))
        self.ui.fld_bought.setText(str(total_bought))

        
        


    def toProf(self):
        self.ui.pages.setCurrentWidget(self.ui.prof_page)
        
        self.ui.line_ID_prof.setText(currentUser['ID'])
        self.ui.line_NAME_prof.setText(currentUser['name'])
        self.ui.line_TITLE_prof.setText(currentUser['title'])
        self.ui.line_AMOUNT_prof.setText(format((currentUser['amount']),'.2f'))
        self.ui.line_PASSWORD_prof.setText(currentUser['password'])
        self.ui.line_BLOCK_prof.setCheckState(Qt.Checked) if currentUser["block"] else self.ui.line_BLOCK_prof.setCheckState(Qt.Unchecked)
        self.ui.line_QR_prof.setText(currentUser['qr'])
    def toProd(self):
        self.ui.pages.setCurrentWidget(self.ui.prod_page)
        self.clearTable(self.ui.ProdList)
        query = f'SELECT * FROM Products'
        cur.execute(query)
        res = cur.fetchall()
        self.ui.ProdList.setRowCount(len(res))
        for i,item in enumerate(res):
            for j in range(len(item)):
                prod = QTableWidgetItem(str(item[j]))
                prod.setTextAlignment(Qt.AlignCenter) if j in (0,2,3,4,5) else prod.setTextAlignment(Qt.AlignLeft)
                self.ui.ProdList.setItem(i,j,prod)
            self.ui.ProdList.setItem(i,6,QTableWidgetItem(''))
    def toUser(self):
        self.ui.pages.setCurrentWidget(self.ui.user_page)
        self.ui.Users.setCurrentIndex(0)
    
    def getCurrentUserInfo(self,user):
        global currentUser
        currentUser['ID']= str(user[0])
        currentUser['name'] = user[1]
        currentUser['title'] = user[2]
        currentUser['amount'] = user[3]
        currentUser['password'] = user[4]
        currentUser['block'] = bool(user[5])
        currentUser['qr'] = user[6]
        self.ui.gebruiker_fld.setText(user[1])
        self.ui.teGoed_fld.setText(format(user[3], '.2f'))

        if user[2] == 'Bestuur':
            self.ui.user_btn.show()
            self.ui.prod_btn.show()
        else:
            self.ui.user_btn.hide()
            self.ui.prod_btn.hide()

    def getItem(self):
        self.ui.ERROR_ITMFLD.clear()
        item = self.ui.item_fld.text()
        if item != "":
            self.ui.item_fld.clear()
            query = f"SELECT * FROM Products WHERE ID = \"{item}\""
            cur.execute(query)
            result = cur.fetchone()

            if result != None:
                incart = False
                incart_row = 0
                product = {
                    "ID"    : result[0],
                    "name"  : result[1],
                    "Price" : result[2]
                }

                rows = self.ui.cart_fld.rowCount()
                for i in range(rows):
                    if product['ID'] == self.ui.cart_fld.item(i,0).text():
                        incart = True
                        incart_row = i
                
                if not incart:
                    self.ui.cart_fld.setRowCount((rows + 1))

                    itemId = QTableWidgetItem()
                    itemName = QTableWidgetItem()
                    itemQty = QTableWidgetItem()
                    itemPrice = QTableWidgetItem()
                    itemTotaal = QTableWidgetItem()
                    itemQty.setTextAlignment(Qt.AlignCenter)
                    itemPrice.setTextAlignment(Qt.AlignCenter)

                    itemId.setText(str(product['ID']))
                    itemName.setText(str(product['name']))
                    itemQty.setText(str(1))
                    itemPrice.setText(format(product['Price'],'.2f'))
                    itemTotaal.setText(format(product['Price'], '.2f'))

                    self.ui.cart_fld.setItem(rows,0,itemId)
                    self.ui.cart_fld.setItem(rows,1,itemName)
                    self.ui.cart_fld.setItem(rows,2,itemQty)
                    self.ui.cart_fld.setItem(rows,3,itemPrice)
                    self.ui.cart_fld.setItem(rows,4,itemTotaal)
                else:
                    qty = int(self.ui.cart_fld.item(incart_row,2).text()) + 1
                    self.ui.cart_fld.item(incart_row,2).setText(str(qty))
                    totaal = float(self.ui.cart_fld.item(incart_row,3).text()) * qty
                    self.ui.cart_fld.item(incart_row,4).setText(format(totaal,'.2f'))
                tot = 0.0
                for j in range(self.ui.cart_fld.rowCount()):
                    tot = tot + float(self.ui.cart_fld.item(j,4).text())
                self.ui.totaal_fld.setText(format(tot,'.2f'))
            else:
                self.ui.ERROR_ITMFLD.setText("[INFO] Product niet gevonden")
            self.ui.item_fld.setFocus()
        else:
            self.pay()

    def deleteItemRow(self):
        row = self.ui.cart_fld.row(self.ui.cart_fld.selectedItems()[0])
        qty = int(self.ui.cart_fld.item(row, 2).text())
        if  qty > 1:
            qty = qty - 1
            self.ui.cart_fld.item(row, 2).setText(str(qty))
            totaal = float(self.ui.cart_fld.item(row,3).text()) * qty
            self.ui.cart_fld.item(row,4).setText(format(totaal,'.2f'))

            tot = 0.0
            for j in range(self.ui.cart_fld.rowCount()):
                tot = tot + float(self.ui.cart_fld.item(j,4).text())
            self.ui.totaal_fld.setText(format(tot,'.2f'))
        elif qty == 1:
            self.ui.cart_fld.removeRow(row)
            tot = 0.0
            for j in range(self.ui.cart_fld.rowCount()):
                tot = tot + float(self.ui.cart_fld.item(j,4).text())
            self.ui.totaal_fld.setText(format(tot,'.2f'))

    def pay(self):
        global starttime
        global stoptime
        
        if self.ui.cart_fld.rowCount() != 0:
            stoptime = time.time()
            genoeg = False
            tot = float(self.ui.totaal_fld.text())
            res = currentUser['amount'] - tot
            if   currentUser['title'] == 'Bestuur':
                genoeg = True if res >= -10.0 else False
            elif currentUser['title'] == 'Commissie':
                genoeg = True if res >= -5.0 else False
            else:
                genoeg = True if res >=  0.0 else False

            if(genoeg):
                currentUser['amount'] = currentUser['amount'] - tot
                self.ui.teGoed_fld.setText(format(currentUser['amount'],'.2f'))
                query = f'UPDATE Users SET Amount = {currentUser["amount"]} WHERE ID = {currentUser["ID"]}'
                cur.execute(query)

                for i in range(self.ui.cart_fld.rowCount()):
                    
                    product = { 
                        'ID'    :       self.ui.cart_fld.item(i,0).text() ,
                        'NAAM'  :       self.ui.cart_fld.item(i,1).text() ,
                        'QTY'   :  int( self.ui.cart_fld.item(i,2).text()),
                        'PRIJS' :float( self.ui.cart_fld.item(i,3).text()),
                        'TOTAAL':float( self.ui.cart_fld.item(i,4).text())
                    }
                    fetchQuery = f'SELECT Stock, Purchase FROM Products WHERE ID = \'{product["ID"]}\''
                    cur.execute(fetchQuery)
                    result = cur.fetchone()
                    product['STOCK'] = result[0] - product['QTY']
                    product['PURCH'] = result[1] + product['QTY']
                    query= f'''
                    UPDATE Products
                    SET Stock = {product["STOCK"]}, Purchase = {product["PURCH"]}
                    WHERE ID = \'{product["ID"]}\';

                    INSERT INTO History (ID, Username, Amount, SKU, Product, Price, Date) 
                    VALUES (\'{currentUser["ID"]}\', \'{currentUser["name"]}\', \'{product["QTY"]}\', \'{product["ID"]}\', \'{product["NAAM"]}\', {product["TOTAAL"]},\'{datetime.date.today().strftime("%d/%m/%Y")}\');
                    '''
                    cur.executescript(query)
                KKdb.commit()
                
                self.ui.ERROR_ITMFLD.setText(f"[SUCCES] Producten zijn afgerekend!\ntime: {stoptime - starttime}")
                self.clearTable(self.ui.cart_fld)
                starttime = time.time()
            else:
                self.ui.ERROR_ITMFLD.setText('[INFO] Er staat niet voldoende geld op je account!')
        else:
            self.ui.ERROR_ITMFLD.setText('[INFO]\tEr staan zitten geen producten\n\tin de winkelwagen!')        

    def addProd(self):
        rows = self.ui.ProdList.rowCount()
        self.ui.ProdList.setRowCount(rows + 1)
        self.ui.ProdList.setItem(rows,0,QTableWidgetItem('Nieuw product'))
        self.ui.ProdList.setItem(rows, 6,QTableWidgetItem(str(True)))
    
    def updateProducts(self):
        try:
            for i in range(self.ui.ProdList.rowCount()):
                id      =       self.ui.ProdList.item(i, 0).text()
                name    =       self.ui.ProdList.item(i, 1).text()
                prijs   = float(self.ui.ProdList.item(i, 2).text())
                stock   =   int(self.ui.ProdList.item(i, 3).text())
                purch   =   int(self.ui.ProdList.item(i, 4).text())
                date    =       datetime.date.today().strftime('%d/%m/%Y')
                new     =  bool(self.ui.ProdList.item(i, 6).text())

                if not new:
                    query = f'UPDATE Products SET Name = \'{name}\', Price = {prijs}, Stock = {stock}, Purchase = {purch}, Date = \'{date}\' WHERE ID = \'{id}\''
                else:
                    query = f'INSERT INTO Products (ID, Name, Price, Stock, Purchase, Date) VALUES ({id},\'{name}\',{prijs},{stock},{purch},\'{date}\')'
                cur.execute(query)
            KKdb.commit()
            self.ui.ERROR_PROD.setText("[SUCCES] De producten zijn geweizigd")
        except Exception:
            self.toProd()
            self.ui.ERROR_PROD.setText("[ERROR] Het weizigen van de producten is niet gelukt")

    def deleteProdRow(self):
        selection = self.ui.ProdList.selectedItems()
        
        query = f'DELETE FROM Products WHERE ID = {selection[0].text()}'
        cur.execute(query)
        KKdb.commit()

        self.clearTable(self.ui.ProdList)
        query = f'SELECT * FROM Products'
        cur.execute(query)
        res = cur.fetchall()
        self.ui.ProdList.setRowCount(len(res))
        for i,item in enumerate(res):
            for j in range(len(item)):
                self.ui.ProdList.setItem(i,j,QTableWidgetItem(str(item[j])))
            self.ui.ProdList.setItem(i,6,QTableWidgetItem(''))
        
    def toEditUser(self):
        self.ui.Users.setCurrentWidget(self.ui.EditUser_page)
        self.ui.line_ID.clear()
        self.ui.line_NAME.clear()
        self.ui.line_TITLE.setCurrentIndex(0)
        self.ui.line_AMOUNT.clear()
        self.ui.line_PASSWORD.clear()
        self.ui.line_BLOCK.setCheckState(Qt.Unchecked)
        self.ui.line_QR.clear()
        self.ui.line_ID.setFocus()
    def toNewUser(self):
        self.ui.Users.setCurrentWidget(self.ui.NewUser_page)
        self.ui.line_ID_ADD.clear()
        self.ui.line_NAME_ADD.clear()
        self.ui.line_TITLE_ADD.setCurrentIndex(0)
        self.ui.line_AMOUNT_ADD.clear()
        self.ui.line_PASSWORD_ADD.clear()
        self.ui.line_BLOCK_ADD.setCheckState(Qt.Unchecked)
        self.ui.line_QR_ADD.clear()
        self.ui.line_ID_ADD.setFocus()
    def toUpdateUser(self):
        self.ui.Users.setCurrentWidget(self.ui.UpdateUser_page)
        self.ui.INC_line_ID.clear()
        self.ui.INC_line_AMOUNT.clear()
        self.ui.INC_line_INC.clear()
        self.ui.INC_line_AMOUNT_2.clear()
        self.ui.INC_line_ID.setFocus()
    
    def getUserInfo(self):
        user = {
            'ID': self.ui.line_ID.text()
        }
        query = f'SELECT * FROM Users WHERE ID = {user["ID"]}'
        cur.execute(query)
        result = cur.fetchone()

        user['Name'] = result[1]
        user['Title'] = result[2]
        user['Amount'] = result[3]
        user['Pass'] = result[4]
        user['Block'] = result[5]
        user['QR'] = result[6]

        self.ui.line_NAME.setText(user['Name'])
        if user['Title'] == 'Bestuur': title = 2
        elif user['Title'] == 'Commissie': title = 1
        else: title = 0
        self.ui.line_TITLE.setCurrentIndex(title)
        self.ui.line_AMOUNT.setText(format((user['Amount']),'.2f'))
        self.ui.line_PASSWORD.setText(user['Pass'])
        self.ui.line_BLOCK.setCheckState(Qt.Checked) if user["Block"] else self.ui.line_BLOCK.setCheckState(Qt.Unchecked)
        self.ui.line_QR.setText(user['QR'])
    def updateUserInfo(self):
        user = {
            'ID'    : str(self.ui.line_ID.text()),
            'NAME'  : str(self.ui.line_NAME.text()),
            'TITLE' : self.ui.line_TITLE.currentText(),
            'AMOUNT': format(float(self.ui.line_AMOUNT.text()),".2f"),
            'PASS'  : str(self.ui.line_PASSWORD.text()),
            'BLOCK' : True if self.ui.line_BLOCK.checkState() == Qt.Checked else False,
            'QR-code': str(self.ui.line_QR.text())
        }
        query = f'SELECT ID FROM Users WHERE qrCodes = \'{user["QR-code"]}\''
        cur.execute(query)
        result = cur.fetchone()
        # print(str(result[0]) == user['ID'])
        if (result == None) or (str(result[0])==user['ID']):
            query = f'UPDATE Users SET Name = \'{user["NAME"]}\', Title = \'{user["TITLE"]}\', Amount = {user["AMOUNT"]}, Password = \'{user["PASS"]}\', Block = {user["BLOCK"]}, qrCodes = \'{user["QR-code"]}\' WHERE ID = {user["ID"]}'
            cur.execute(query)
            KKdb.commit()
            self.ui.ERROR_UPDUSR.setText(f'[INFO] account van {user["NAME"]}  is succesvol bewerkt')
        else:
            self.ui.ERROR_UPDUSR.setText('[INFO] QR-code is onbruikbaar, graag een andere gebruiken')
    def addUser(self):
        self.resetInfoLines()
        new = {
            "ID"    : self.ui.line_ID_ADD.text(),
            "NAAM"  : self.ui.line_NAME_ADD.text(),
            "TITLE" : self.ui.line_TITLE_ADD.currentText(),
            "AMOUNT": self.ui.line_AMOUNT_ADD.text(),
            "PASS"  : self.ui.line_PASSWORD_ADD.text(),
            "BLOCK" : True if self.ui.line_BLOCK_ADD.checkState() == Qt.Checked else False,
            "QR"    : self.ui.line_QR_ADD.text()
        }
        query = f'SELECT ID,qrCodes FROM Users WHERE ID = \'{new["ID"]}\' OR qrCodes = \'{new["QR"]}\''
        cur.execute(query)
        result = cur.fetchone()
        print(result)
        if result == None:
            query = f'INSERT INTO Users (ID, Name, Title, Amount, Password, Block, qrCodes) VALUES (\'{new["ID"]}\', \'{new["NAAM"]}\', \'{new["TITLE"]}\', {new["AMOUNT"]}, \'{new["PASS"]}\', {new["BLOCK"]},\'{new["QR"]}\')'
            cur.execute(query)
            KKdb.commit()

            self.ui.line_ID_ADD.clear()
            self.ui.line_NAME_ADD.clear()
            self.ui.line_TITLE_ADD.setCurrentIndex(0)
            self.ui.line_AMOUNT_ADD.clear()
            self.ui.line_PASSWORD_ADD.clear()
            self.ui.line_BLOCK_ADD.setCheckState(Qt.Unchecked)
            self.ui.line_QR_ADD.clear()
            self.ui.line_ID_ADD.setFocus()
            self.ui.ERROR_ADDUSR.setText('[INFO] Nieuwe gebruiker succesvol toegevoegd!')
        else:
            if new['ID'] == str(result[0]):
                self.ui.ERROR_ADDUSR.setText('[INFO] Student heeft al een account!')
            elif new['QR'] == result[1]:
                self.ui.ERROR_ADDUSR.setText('[INFO] QR-code is onbruikbaar, graag een andere ingeven')

    def getUserAmount(self):
        id = self.ui.INC_line_ID.text()
        query = f'SELECT Amount FROM Users WHERE ID = \'{id}\''
        cur.execute(query)
        res = cur.fetchone()[0]
        self.ui.INC_line_AMOUNT.setText(format(res,'.2f'))
        self.ui.INC_line_INC.setFocus()
    def increaseAmount(self):
        currentVal  = float(self.ui.INC_line_AMOUNT.text())
        addVal      = float(self.ui.INC_line_INC.text()) if self.ui.INC_line_INC.text() != '' else 0.
        newVal      = currentVal + addVal
        self.ui.INC_line_AMOUNT_2.setText(str(newVal))
    def saveNewAmount(self):
        id = self.ui.INC_line_ID.text()
        val = self.ui.INC_line_AMOUNT_2.text()
        query = f'UPDATE Users SET Amount = {val} WHERE ID = {id}'
        cur.execute(query)
        KKdb.commit()
        self.ui.INC_line_AMOUNT.setText(self.ui.INC_line_AMOUNT_2.text())
        self.ui.INC_line_INC.clear()
        self.ui.INC_line_AMOUNT_2.clear()

    def resetInfoLines(self):
        self.ui.ERROR_STDNR.clear()
        self.ui.ERROR_PSWRD.clear()
        self.ui.ERROR_QRFLD.clear()
        self.ui.ERROR_ADDUSR.clear()
        self.ui.ERROR_UPDUSR.clear()

    def clearTable(self, table):
        table.clearContents()
        table.setRowCount(0)
        if table == self.ui.cart_fld:
            self.ui.totaal_fld.setText('0.00')

    def deleteRow(self):
        if self.ui.pages.currentWidget() == self.ui.buy_page:
            self.deleteItemRow()
            self.ui.item_fld.setFocus()
        elif self.ui.pages.currentWidget() == self.ui.prod_page:
            self.deleteProdRow()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    with open("style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)


    sys.exit(app.exec())

