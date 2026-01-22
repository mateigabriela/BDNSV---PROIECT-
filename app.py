from flask import Flask, render_template_string, jsonify, request
import pymongo
import random
import numpy as np
from datetime import datetime
import time


app = Flask(__name__)

try:
    client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
    client.admin.command('ping')
    db = client["moto_shop_db"]
    print("✅ Conectat la MongoDB!")
except Exception as e:
    print(f"⚠️ ATENȚIE: Nu s-a putut conecta la MongoDB: {e}")
    db = None

HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Motocycle Shop</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: #f5f5f5; 
            color: #333; 
        }
        
        /* HEADER */
        header {
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: white;
            padding: 20px 40px;
            text-align: center;
        }
        header h1 { font-size: 2em; margin-bottom: 5px; }
        header p { color: #aaa; font-size: 0.9em; }
        
        /* LAYOUT */
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        
        /* TABS */
        .tabs {
            display: flex;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .tab {
            flex: 1;
            padding: 15px;
            text-align: center;
            background: #eee;
            border: none;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        .tab:hover { background: #ddd; }
        .tab.active { background: #3498db; color: white; }
        
        /* PANELS */
        .panel { display: none; }
        .panel.active { display: block; }
        
        /* CARDS */
        .card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }
        .card h2 { 
            color: #2c3e50; 
            border-bottom: 2px solid #3498db; 
            padding-bottom: 10px; 
            margin-bottom: 15px;
        }
        .card h3 { color: #3498db; margin: 15px 0 10px; }
        
        /* STATS */
        .stats-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-box {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-box.green { background: linear-gradient(135deg, #27ae60, #2ecc71); }
        .stat-box.orange { background: linear-gradient(135deg, #e67e22, #f39c12); }
        .stat-box.purple { background: linear-gradient(135deg, #9b59b6, #8e44ad); }
        .stat-value { font-size: 2em; font-weight: bold; }
        .stat-label { font-size: 0.85em; opacity: 0.9; margin-top: 5px; }
        
        /* BUTTONS */
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
            margin: 5px;
        }
        .btn-primary { background: #3498db; color: white; }
        .btn-primary:hover { background: #2980b9; }
        .btn-success { background: #27ae60; color: white; }
        .btn-success:hover { background: #219a52; }
        .btn-warning { background: #f39c12; color: white; }
        .btn-danger { background: #e74c3c; color: white; }
        .btn-danger:hover { background: #c0392b; }
        .btn-sm { padding: 5px 10px; font-size: 0.85em; }
        
        /* FORMS */
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 600; color: #2c3e50; }
        .form-group input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1em;
        }
        .form-group input:focus { border-color: #3498db; outline: none; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        
        /* MODAL */
        .modal {
            display: none;
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        .modal.active { display: flex; }
        .modal-content {
            background: white;
            padding: 25px;
            border-radius: 10px;
            width: 90%;
            max-width: 500px;
            max-height: 90vh;
            overflow-y: auto;
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        }
        .modal-header h3 { color: #2c3e50; }
        .modal-close {
            background: none;
            border: none;
            font-size: 1.5em;
            cursor: pointer;
            color: #888;
        }
        .modal-close:hover { color: #e74c3c; }
        
        /* PRODUCTS */
        .products-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
        }
        .product-card {
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            transition: transform 0.3s;
        }
        .product-card:hover { transform: translateY(-5px); }
        .product-body { padding: 15px; }
        .product-name { font-weight: bold; color: #2c3e50; }
        .product-price { color: #27ae60; font-size: 1.3em; font-weight: bold; margin: 10px 0; }
        .product-stock { 
            font-size: 0.85em; 
            padding: 3px 8px; 
            border-radius: 3px;
            display: inline-block;
        }
        .stock-ok { background: #d4edda; color: #155724; }
        .stock-low { background: #fff3cd; color: #856404; }
        .stock-out { background: #f8d7da; color: #721c24; }
        .btn-buy {
            width: 100%;
            margin-top: 10px;
            padding: 10px;
            background: #27ae60;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }
        .btn-buy:hover { background: #219a52; }
        .btn-buy:disabled { background: #ccc; cursor: not-allowed; }
        
        /* USERS TABLE */
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th { background: #3498db; color: white; }
        tr:hover { background: #f5f5f5; }
        
        /* DOCUMENTATION */
        .doc-section {
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 15px 0;
            border-radius: 0 5px 5px 0;
        }
        .doc-section h4 { color: #3498db; margin-bottom: 10px; }
        code {
            background: #2c3e50;
            color: #2ecc71;
            padding: 10px;
            border-radius: 5px;
            display: block;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
            overflow-x: auto;
        }
        
        /* RESULT BOX */
        .result-box {
            background: #e8f4fd;
            border: 1px solid #3498db;
            border-radius: 5px;
            padding: 15px;
            margin-top: 15px;
        }
        .result-item {
            padding: 8px;
            background: white;
            margin: 5px 0;
            border-radius: 3px;
            display: flex;
            justify-content: space-between;
        }
        
        /* TOAST */
        .toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #27ae60;
            color: white;
            padding: 15px 25px;
            border-radius: 5px;
            transform: translateX(400px);
            transition: transform 0.3s;
            z-index: 1000;
        }
        .toast.show { transform: translateX(0); }
        .toast.error { background: #e74c3c; }
    </style>
</head>
<body>

    <header>
        <h1>Motocycle Shop</h1>
    </header>

    <div class="container">
        
        <!-- STATISTICI -->
        <div class="stats-row">
            <div class="stat-box">
                <div class="stat-value" id="stat-products">-</div>
                <div class="stat-label">Produse</div>
            </div>
            <div class="stat-box green">
                <div class="stat-value" id="stat-orders">-</div>
                <div class="stat-label">Comenzi</div>
            </div>
            <div class="stat-box orange">
                <div class="stat-value" id="stat-revenue">-</div>
                <div class="stat-label">Venituri (€)</div>
            </div>
            <div class="stat-box purple">
                <div class="stat-value" id="stat-users">-</div>
                <div class="stat-label">Utilizatori</div>
            </div>
        </div>
        
        <!-- TABS NAVIGARE -->
        <div class="tabs">
            <button class="tab active" onclick="showPanel('produse')">Produse</button>
            <button class="tab" onclick="showPanel('users')">Utilizatori</button>
            <button class="tab" onclick="showPanel('functii')">Functionalitati</button>
        </div>

        <!-- PANEL PRODUSE -->
        <div class="panel active" id="panel-produse">
            <div class="card">
                <h2>Catalog Motociclete</h2>
                <button class="btn btn-primary" onclick="initDB()">Reseteaza Baza de Date</button>
                <span id="product-count" style="margin-left: 15px; color: #888;"></span>
                <div class="products-grid" id="products-grid" style="margin-top: 20px;"></div>
            </div>
        </div>

        <!-- PANEL UTILIZATORI -->
        <div class="panel" id="panel-users">
            <div class="card">
                <h2>Gestiune Utilizatori (CRUD)</h2>
                <p style="color: #888; margin-bottom: 15px;">
                    <strong>Schema Design:</strong> Adresele sunt EMBEDDED in documentul user (array 1:N limitat - max 3 adrese)
                </p>
                <button class="btn btn-success" onclick="openUserModal()">Adauga Utilizator</button>
                <table id="users-table" style="margin-top: 15px;">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Nume</th>
                            <th>Email</th>
                            <th>Adrese Livrare</th>
                            <th>Actiuni</th>
                        </tr>
                    </thead>
                    <tbody id="users-tbody"></tbody>
                </table>
            </div>
            
            <div class="card">
                <h2>Ultimele Comenzi</h2>
                <p style="color: #888; margin-bottom: 15px;">
                    <strong>Schema Design:</strong> SNAPSHOT PATTERN - prețul este copiat la momentul comenzii
                </p>
                <table>
                    <thead>
                        <tr>
                            <th>Cod Comandă</th>
                            <th>Produs</th>
                            <th>Preț Snapshot</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody id="orders-tbody"></tbody>
                </table>
            </div>
        </div>

        <!-- PANEL FUNCTIONALITATI -->
        <div class="panel" id="panel-functii">
            <div class="card">
                <h2>Testare Functionalitati MongoDB</h2>
                
                <div style="margin: 20px 0;">
                    <button class="btn btn-success" onclick="vectorSearch()">Vector Search (AI)</button>
                    <button class="btn btn-primary" onclick="testPerformance()">Test Indexare</button>
                    <button class="btn btn-warning" onclick="showAggregation()">Aggregation Pipeline</button>
                </div>
                
                <h3 style="margin-top:30px;">Scaling Strategies (Demo)</h3>
                <div style="margin: 20px 0;">
                    <button class="btn" style="background:#9c27b0;color:white;" onclick="showReplicationDemo()">Replication Demo</button>
                    <button class="btn" style="background:#ff5722;color:white;" onclick="showShardingDemo()">Sharding Simulation</button>
                    <button class="btn" style="background:#607d8b;color:white;" onclick="showScalingComparison()">Vertical vs Horizontal</button>
                </div>
                
                <div id="results-container"></div>
            </div>
        </div>

    </div>

    <!-- MODAL UTILIZATOR -->
    <div class="modal" id="userModal">
        <div class="modal-content">
            <div class="modal-header">
                <h3 id="modalTitle">Adauga Utilizator</h3>
                <button class="modal-close" onclick="closeUserModal()">&times;</button>
            </div>
            <form id="userForm" onsubmit="saveUser(event)">
                <input type="hidden" id="editUserId">
                <div class="form-group">
                    <label>Nume Complet</label>
                    <input type="text" id="userName" required placeholder="Ex: Ion Popescu">
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" id="userEmail" required placeholder="Ex: ion@email.ro">
                </div>
                
                <h4 style="margin: 20px 0 10px; color: #2c3e50;">Adrese de Livrare (max 3)</h4>
                <div id="addressesContainer">
                    <div class="address-block" data-index="0">
                        <div class="form-row">
                            <div class="form-group">
                                <label>Eticheta</label>
                                <input type="text" class="addr-label" placeholder="Ex: Acasa, Birou">
                            </div>
                            <div class="form-group">
                                <label>Oras</label>
                                <input type="text" class="addr-city" required placeholder="Ex: Bucuresti">
                            </div>
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label>Strada</label>
                                <input type="text" class="addr-street" required placeholder="Ex: Str. Libertatii 10">
                            </div>
                            <div class="form-group">
                                <label>Cod Postal</label>
                                <input type="text" class="addr-zip" placeholder="Ex: 010101">
                            </div>
                        </div>
                    </div>
                </div>
                <button type="button" class="btn btn-primary btn-sm" onclick="addAddressField()" style="margin: 10px 0;">+ Adauga alta adresa</button>
                
                <div style="display: flex; gap: 10px; margin-top: 20px;">
                    <button type="submit" class="btn btn-success" style="flex:1;">Salveaza</button>
                    <button type="button" class="btn btn-danger" onclick="closeUserModal()">Anuleaza</button>
                </div>
            </form>
        </div>
    </div>

    <div class="toast" id="toast"></div>

    <script>
        // INIT
        document.addEventListener('DOMContentLoaded', () => {
            loadProducts();
            loadStats();
            loadUsers();
            loadOrders();
        });

        // SWITCH PANELS
        function showPanel(name) {
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.getElementById('panel-' + name).classList.add('active');
            event.target.classList.add('active');
            
            if (name === 'users') {
                loadUsers();
                loadOrders();
            }
        }

        // TOAST
        function showToast(msg, type = 'success') {
            const toast = document.getElementById('toast');
            toast.textContent = msg;
            toast.className = 'toast show ' + type;
            setTimeout(() => toast.classList.remove('show'), 3000);
        }

        // LOAD STATS
        async function loadStats() {
            try {
                const res = await fetch('/api/stats');
                const data = await res.json();
                document.getElementById('stat-products').textContent = data.total_products;
                document.getElementById('stat-orders').textContent = data.total_orders;
                document.getElementById('stat-revenue').textContent = data.total_revenue.toLocaleString();
                
                const usersRes = await fetch('/api/users');
                const users = await usersRes.json();
                document.getElementById('stat-users').textContent = users.length;
            } catch (e) { console.error(e); }
        }

        // LOAD PRODUCTS
        async function loadProducts() {
            try {
                const res = await fetch('/api/products');
                const products = await res.json();
                document.getElementById('product-count').textContent = products.length + ' produse in catalog';
                
                document.getElementById('products-grid').innerHTML = products.map(p => {
                    const stockClass = p.stock > 3 ? 'stock-ok' : (p.stock > 0 ? 'stock-low' : 'stock-out');
                    const stockText = p.stock > 0 ? p.stock + ' in stoc' : 'Stoc epuizat';
                    return `
                        <div class="product-card">
                            <div class="product-body">
                                <div class="product-name">${p.name}</div>
                                <div class="product-price">${p.price.toLocaleString()} EUR</div>
                                <span class="product-stock ${stockClass}">${stockText}</span>
                                <button class="btn-buy" onclick="buyProduct('${p.moto_id}')" ${p.stock <= 0 ? 'disabled' : ''}>
                                    ${p.stock > 0 ? 'Cumpara' : 'Indisponibil'}
                                </button>
                            </div>
                        </div>
                    `;
                }).join('');
            } catch (e) { console.error(e); }
        }

        // LOAD USERS
        async function loadUsers() {
            try {
                const res = await fetch('/api/users');
                const users = await res.json();
                document.getElementById('users-tbody').innerHTML = users.map(u => {
                    const addresses = u.addresses || [];
                    const addrText = addresses.map(a => `<div><small><strong>${a.label || 'Adresa'}:</strong> ${a.city}, ${a.street}</small></div>`).join('');
                    return `
                        <tr>
                            <td>${u.user_id}</td>
                            <td>${u.name}</td>
                            <td>${u.email}</td>
                            <td>${addrText || '-'}</td>
                            <td>
                                <button class="btn btn-primary btn-sm" onclick="editUser('${u.user_id}')">Edit</button>
                                <button class="btn btn-danger btn-sm" onclick="deleteUser('${u.user_id}')">Sterge</button>
                            </td>
                        </tr>
                    `;
                }).join('');
            } catch (e) { console.error(e); }
        }

        // ADDRESS FIELD MANAGEMENT
        let addressCount = 1;
        
        function addAddressField() {
            if (addressCount >= 3) {
                showToast('Maxim 3 adrese permise!', 'error');
                return;
            }
            const container = document.getElementById('addressesContainer');
            const newBlock = document.createElement('div');
            newBlock.className = 'address-block';
            newBlock.dataset.index = addressCount;
            newBlock.innerHTML = `
                <hr style="margin: 15px 0; border-color: #eee;">
                <div class="form-row">
                    <div class="form-group">
                        <label>Eticheta</label>
                        <input type="text" class="addr-label" placeholder="Ex: Acasa, Birou">
                    </div>
                    <div class="form-group">
                        <label>Oras</label>
                        <input type="text" class="addr-city" placeholder="Ex: Bucuresti">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Strada</label>
                        <input type="text" class="addr-street" placeholder="Ex: Str. Libertatii 10">
                    </div>
                    <div class="form-group">
                        <label>Cod Postal</label>
                        <input type="text" class="addr-zip" placeholder="Ex: 010101">
                    </div>
                </div>
                <button type="button" class="btn btn-danger btn-sm" onclick="removeAddressField(this)">Sterge adresa</button>
            `;
            container.appendChild(newBlock);
            addressCount++;
        }
        
        function removeAddressField(btn) {
            btn.parentElement.remove();
            addressCount--;
        }

        // MODAL FUNCTIONS
        function openUserModal(userId = null) {
            document.getElementById('userModal').classList.add('active');
            document.getElementById('userForm').reset();
            document.getElementById('editUserId').value = '';
            document.getElementById('modalTitle').textContent = 'Adauga Utilizator';
            // Reset addresses
            const container = document.getElementById('addressesContainer');
            container.innerHTML = `
                <div class="address-block" data-index="0">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Eticheta</label>
                            <input type="text" class="addr-label" placeholder="Ex: Acasa, Birou">
                        </div>
                        <div class="form-group">
                            <label>Oras</label>
                            <input type="text" class="addr-city" required placeholder="Ex: Bucuresti">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Strada</label>
                            <input type="text" class="addr-street" required placeholder="Ex: Str. Libertatii 10">
                        </div>
                        <div class="form-group">
                            <label>Cod Postal</label>
                            <input type="text" class="addr-zip" placeholder="Ex: 010101">
                        </div>
                    </div>
                </div>
            `;
            addressCount = 1;
        }

        function closeUserModal() {
            document.getElementById('userModal').classList.remove('active');
        }

        // EDIT USER
        async function editUser(userId) {
            try {
                const res = await fetch('/api/users');
                const users = await res.json();
                const user = users.find(u => u.user_id === userId);
                
                if (user) {
                    // Setam ID-ul pentru editare
                    document.getElementById('editUserId').value = user.user_id;
                    document.getElementById('userName').value = user.name || '';
                    document.getElementById('userEmail').value = user.email || '';
                    document.getElementById('modalTitle').textContent = 'Editeaza Utilizator';
                    
                    // Populate addresses
                    const container = document.getElementById('addressesContainer');
                    container.innerHTML = '';
                    const addresses = user.addresses || [];
                    addressCount = 0;
                    
                    if (addresses.length === 0) {
                        // Daca nu are adrese, adaugam un bloc gol
                        container.innerHTML = `
                            <div class="address-block" data-index="0">
                                <div class="form-row">
                                    <div class="form-group">
                                        <label>Eticheta</label>
                                        <input type="text" class="addr-label" placeholder="Ex: Acasa, Birou">
                                    </div>
                                    <div class="form-group">
                                        <label>Oras</label>
                                        <input type="text" class="addr-city" required placeholder="Ex: Bucuresti">
                                    </div>
                                </div>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label>Strada</label>
                                        <input type="text" class="addr-street" required placeholder="Ex: Str. Libertatii 10">
                                    </div>
                                    <div class="form-group">
                                        <label>Cod Postal</label>
                                        <input type="text" class="addr-zip" placeholder="Ex: 010101">
                                    </div>
                                </div>
                            </div>
                        `;
                        addressCount = 1;
                    } else {
                        addresses.forEach((addr, idx) => {
                            const block = document.createElement('div');
                            block.className = 'address-block';
                            block.dataset.index = idx;
                            block.innerHTML = `
                                ${idx > 0 ? '<hr style="margin: 15px 0; border-color: #eee;">' : ''}
                                <div class="form-row">
                                    <div class="form-group">
                                        <label>Eticheta</label>
                                        <input type="text" class="addr-label" value="${addr.label || ''}" placeholder="Ex: Acasa, Birou">
                                    </div>
                                    <div class="form-group">
                                        <label>Oras</label>
                                        <input type="text" class="addr-city" value="${addr.city || ''}" placeholder="Ex: Bucuresti">
                                    </div>
                                </div>
                                <div class="form-row">
                                    <div class="form-group">
                                        <label>Strada</label>
                                        <input type="text" class="addr-street" value="${addr.street || ''}" placeholder="Ex: Str. Libertatii 10">
                                    </div>
                                    <div class="form-group">
                                        <label>Cod Postal</label>
                                        <input type="text" class="addr-zip" value="${addr.zip || ''}" placeholder="Ex: 010101">
                                    </div>
                                </div>
                                ${idx > 0 ? '<button type="button" class="btn btn-danger btn-sm" onclick="removeAddressField(this)">Sterge adresa</button>' : ''}
                            `;
                            container.appendChild(block);
                            addressCount++;
                        });
                    }
                    
                    // Afisam modalul
                    document.getElementById('userModal').classList.add('active');
                }
            } catch (e) { showToast('Eroare la incarcare!', 'error'); }
        }

        // SAVE USER (CREATE / UPDATE)
        async function saveUser(event) {
            event.preventDefault();
            
            const userId = document.getElementById('editUserId').value;
            
            // Collect addresses
            const addressBlocks = document.querySelectorAll('.address-block');
            const addresses = [];
            addressBlocks.forEach(block => {
                const label = block.querySelector('.addr-label').value;
                const city = block.querySelector('.addr-city').value;
                const street = block.querySelector('.addr-street').value;
                const zip = block.querySelector('.addr-zip').value;
                if (city && street) {
                    addresses.push({ label: label || 'Adresa', city, street, zip });
                }
            });
            
            const userData = {
                name: document.getElementById('userName').value,
                email: document.getElementById('userEmail').value,
                addresses: addresses
            };

            try {
                let res;
                if (userId) {
                    res = await fetch('/api/users/' + userId, {
                        method: 'PUT',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(userData)
                    });
                } else {
                    res = await fetch('/api/users', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(userData)
                    });
                }
                
                const data = await res.json();
                showToast(data.message, data.success ? 'success' : 'error');
                
                if (data.success) {
                    closeUserModal();
                    loadUsers();
                    loadStats();
                }
            } catch (e) { showToast('Eroare la salvare!', 'error'); }
        }

        // DELETE USER
        async function deleteUser(userId) {
            if (!confirm('Esti sigur ca vrei sa stergi acest utilizator?')) return;
            
            try {
                const res = await fetch('/api/users/' + userId, { method: 'DELETE' });
                const data = await res.json();
                showToast(data.message, data.success ? 'success' : 'error');
                loadUsers();
                loadStats();
            } catch (e) { showToast('Eroare la stergere!', 'error'); }
        }

        // LOAD ORDERS
        async function loadOrders() {
            try {
                const res = await fetch('/api/orders');
                const orders = await res.json();
                document.getElementById('orders-tbody').innerHTML = orders.length > 0 
                    ? orders.map(o => `
                        <tr>
                            <td>${o.order_code}</td>
                            <td>${o.product_name}</td>
                            <td>${o.price_snapshot?.toLocaleString()} €</td>
                            <td><span style="color: green;">${o.status}</span></td>
                        </tr>
                    `).join('')
                    : '<tr><td colspan="4" style="text-align:center; color:#888;">Nu exista comenzi inca</td></tr>';
            } catch (e) { console.error(e); }
        }

        // BUY PRODUCT
        async function buyProduct(motoId) {
            try {
                const res = await fetch('/api/buy', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({id: motoId})
                });
                const data = await res.json();
                showToast(data.message, data.success ? 'success' : 'error');
                loadProducts();
                loadStats();
                loadOrders();
            } catch (e) { showToast('Eroare!', 'error'); }
        }

        // INIT DB
        async function initDB() {
            if (!confirm('Resetezi baza de date?')) return;
            try {
                const res = await fetch('/api/init', { method: 'POST' });
                const data = await res.json();
                showToast('DB resetată: ' + data.products_count + ' produse, ' + data.users_count + ' useri');
                loadProducts();
                loadStats();
                loadUsers();
                loadOrders();
            } catch (e) { showToast('Eroare!', 'error'); }
        }

        // VECTOR SEARCH
        async function vectorSearch() {
            try {
                const res = await fetch('/api/vector-search');
                const data = await res.json();
                document.getElementById('results-container').innerHTML = `
                    <div class="result-box">
                        <h3>Vector Search - Top 5 Rezultate</h3>
                        <p style="color:#666; margin-bottom:10px;">Cautare bazata pe Cosine Similarity</p>
                        ${data.map(d => `
                            <div class="result-item">
                                <span>${d.name} - ${d.price.toLocaleString()} €</span>
                                <strong style="color:#27ae60;">${d.score}% match</strong>
                            </div>
                        `).join('')}
                    </div>
                `;
            } catch (e) { showToast('Eroare!', 'error'); }
        }

        // TEST PERFORMANCE
        async function testPerformance() {
            try {
                const res = await fetch('/api/test-performance');
                const data = await res.json();
                document.getElementById('results-container').innerHTML = `
                    <div class="result-box">
                        <h3>Test Performanta Indexare</h3>
                        <div class="result-item">
                            <span>Fara index</span>
                            <strong style="color:#e74c3c;">${data.without_index.time} ms</strong>
                        </div>
                        <div class="result-item">
                            <span>Cu index pe 'price'</span>
                            <strong style="color:#27ae60;">${data.with_index.time} ms</strong>
                        </div>
                        <p style="text-align:center; margin-top:15px; color:#3498db; font-weight:bold;">
                            Imbunatatire: ${data.improvement}x mai rapid!
                        </p>
                    </div>
                `;
            } catch (e) { showToast('Eroare!', 'error'); }
        }

        // AGGREGATION
        async function showAggregation() {
            try {
                const res = await fetch('/api/aggregation');
                const data = await res.json();
                document.getElementById('results-container').innerHTML = `
                    <div class="result-box">
                        <h3>Aggregation Pipeline - Statistici per Brand</h3>
                        ${data.map(d => `
                            <div class="result-item">
                                <span><strong>${d._id}</strong></span>
                                <span>${d.total_products} produse | Media: ${d.avg_price.toLocaleString()} € | Stoc: ${d.total_stock}</span>
                            </div>
                        `).join('')}
                    </div>
                `;
            } catch (e) { showToast('Eroare!', 'error'); }
        }
        
        // --- SCALING DEMOS ---
        function showReplicationDemo() {
            document.getElementById('results-container').innerHTML = `
                <div class="result-box">
                    <h3>Replica Set Demo</h3>
                    <p><strong>Scenariul:</strong> 3 noduri MongoDB (1 PRIMARY + 2 SECONDARY)</p>
                    
                    <div style="display:flex; gap:20px; margin:20px 0; flex-wrap:wrap;">
                        <div style="background:#4caf50; color:white; padding:20px; border-radius:8px; flex:1; min-width:150px; text-align:center;">
                            <strong>PRIMARY</strong><br>:27017<br>
                            <small>Write Operations</small>
                        </div>
                        <div style="background:#2196f3; color:white; padding:20px; border-radius:8px; flex:1; min-width:150px; text-align:center;">
                            <strong>SECONDARY</strong><br>:27018<br>
                            <small>Read Replica</small>
                        </div>
                        <div style="background:#2196f3; color:white; padding:20px; border-radius:8px; flex:1; min-width:150px; text-align:center;">
                            <strong>SECONDARY</strong><br>:27019<br>
                            <small>Read Replica</small>
                        </div>
                    </div>
                    
                    <h4>Failover Test:</h4>
                    <ol style="line-height:2;">
                        <li>PRIMARY (:27017) primeste toate write-urile</li>
                        <li>SECONDARY-urile replică datele asincron</li>
                        <li>Dacă PRIMARY pică, un SECONDARY devine noul PRIMARY (election)</li>
                        <li>Aplicația se reconectează automat la noul PRIMARY</li>
                    </ol>
                    
                    <h4>Comenzi MongoDB Shell:</h4>
                    <pre style="background:#263238; color:#fff; padding:15px; border-radius:5px; overflow-x:auto;">
rs.status()

rs.stepDown()

db.products.find().readPref("secondary")

db.products.insertOne({...}, { writeConcern: { w: "majority" } })
                    </pre>
                    
                    <h4>Trade-offs:</h4>
                    <ul style="line-height:1.8;">
                        <li><strong>Pro:</strong> High Availability, zero downtime pentru read</li>
                        <li><strong>Con:</strong> Eventual consistency pe SECONDARY (citiri pot fi vechi cu câteva ms)</li>
                        <li><strong>Pro:</strong> Write concern "majority" garantează durabilitate</li>
                        <li><strong>Con:</strong> Latență mai mare pentru write cu w:"majority"</li>
                    </ul>
                </div>
            `;
        }
        
        async function showShardingDemo() {
            try {
                const res = await fetch('/api/sharding-simulation');
                const data = await res.json();
                
                document.getElementById('results-container').innerHTML = `
                    <div class="result-box">
                        <h3>Sharding Simulation</h3>
                        <p><strong>Scenariul:</strong> ${data.total_products} produse distribuite pe 3 shards (shard key: brand)</p>
                        
                        <div style="display:flex; gap:20px; margin:20px 0; flex-wrap:wrap;">
                            ${data.shards.map((shard, i) => `
                                <div style="background:${['#e91e63','#9c27b0','#3f51b5'][i]}; color:white; padding:20px; border-radius:8px; flex:1; min-width:200px;">
                                    <strong>${shard.name}</strong><br>
                                    <span style="font-size:24px;">${shard.products} produse</span><br>
                                    <small>Brands: ${shard.brands.join(', ')}</small>
                                </div>
                            `).join('')}
                        </div>
                        
                        <h4>Query Performance (cu shard key):</h4>
                        <div style="margin:10px 0; padding:10px; background:#e8f5e9; border-radius:5px;">
                            <code>db.products.find({ brand: "Yamaha" })</code><br>
                            <strong>Targeted Query:</strong> Query-ul merge direct la shard-ul care contine Yamaha
                        </div>
                        
                        <h4>Query Performance (fara shard key):</h4>
                        <div style="margin:10px 0; padding:10px; background:#ffebee; border-radius:5px;">
                            <code>db.products.find({ price: { $gt: 5000 } })</code><br>
                            <strong>Scatter-Gather:</strong> Query-ul trebuie trimis la TOATE shard-urile
                        </div>
                        
                        <h4>Alegerea Shard Key - Trade-offs:</h4>
                        <table style="width:100%; border-collapse:collapse; margin:10px 0;">
                            <tr style="background:#f5f5f5;">
                                <th style="border:1px solid #ddd; padding:8px;">Shard Key</th>
                                <th style="border:1px solid #ddd; padding:8px;">Distribuție</th>
                                <th style="border:1px solid #ddd; padding:8px;">Query Efficiency</th>
                            </tr>
                            <tr>
                                <td style="border:1px solid #ddd; padding:8px;">brand (Range)</td>
                                <td style="border:1px solid #ddd; padding:8px;">Poate fi dezechilibrată</td>
                                <td style="border:1px solid #ddd; padding:8px;">Targeted pentru brand queries</td>
                            </tr>
                            <tr>
                                <td style="border:1px solid #ddd; padding:8px;">_id (Hashed)</td>
                                <td style="border:1px solid #ddd; padding:8px;">Uniformă</td>
                                <td style="border:1px solid #ddd; padding:8px;">Scatter-gather pentru range queries</td>
                            </tr>
                            <tr>
                                <td style="border:1px solid #ddd; padding:8px;">{ brand: 1, _id: 1 }</td>
                                <td style="border:1px solid #ddd; padding:8px;">Echilibrată</td>
                                <td style="border:1px solid #ddd; padding:8px;">Optim pentru majoritatea queries</td>
                            </tr>
                        </table>
                    </div>
                `;
            } catch (e) {
                document.getElementById('results-container').innerHTML = `<div class="result-box"><p>Eroare: ${e.message}</p></div>`;
            }
        }
        
        function showScalingComparison() {
            document.getElementById('results-container').innerHTML = `
                <div class="result-box">
                    <h3>Vertical vs Horizontal Scaling</h3>
                    
                    <div style="display:flex; gap:30px; margin:20px 0; flex-wrap:wrap;">
                        <div style="flex:1; min-width:300px; border:2px solid #4caf50; border-radius:10px; padding:20px;">
                            <h4 style="color:#4caf50; margin-top:0;">Vertical Scaling (Scale Up)</h4>
                            <div style="font-size:40px; text-align:center; margin:20px 0;">
                                <span style="display:inline-block; border:2px solid #333; padding:10px; border-radius:5px;">SERVER</span>
                            </div>
                            <p style="text-align:center; color:#666;">Adaugă RAM, CPU, SSD</p>
                            <ul style="line-height:1.8;">
                                <li><strong>Pro:</strong> Simplu de implementat</li>
                                <li><strong>Pro:</strong> Fără modificări în aplicație</li>
                                <li><strong>Con:</strong> Limită hardware (max ~96 cores, 4TB RAM)</li>
                                <li><strong>Con:</strong> Single point of failure</li>
                                <li><strong>Con:</strong> Downtime pentru upgrade</li>
                            </ul>
                            <p style="background:#e8f5e9; padding:10px; border-radius:5px;"><strong>Când folosești:</strong> Aplicații mici-medii, prototipuri, când vrei simplitate</p>
                        </div>
                        
                        <div style="flex:1; min-width:300px; border:2px solid #2196f3; border-radius:10px; padding:20px;">
                            <h4 style="color:#2196f3; margin-top:0;">Horizontal Scaling (Scale Out)</h4>
                            <div style="font-size:40px; text-align:center; margin:20px 0;">
                                <span style="display:inline-block; border:2px solid #333; padding:10px; border-radius:5px; margin:0 5px;">S1</span>
                                <span style="display:inline-block; border:2px solid #333; padding:10px; border-radius:5px; margin:0 5px;">S2</span>
                                <span style="display:inline-block; border:2px solid #333; padding:10px; border-radius:5px; margin:0 5px;">S3</span>
                            </div>
                            <p style="text-align:center; color:#666;">Adaugă mai multe servere</p>
                            <ul style="line-height:1.8;">
                                <li><strong>Pro:</strong> Scalabilitate practic nelimitată</li>
                                <li><strong>Pro:</strong> High Availability (fără single point of failure)</li>
                                <li><strong>Pro:</strong> Zero downtime pentru scaling</li>
                                <li><strong>Con:</strong> Complexitate crescută (sharding, replication)</li>
                                <li><strong>Con:</strong> Necesită planificare shard key</li>
                            </ul>
                            <p style="background:#e3f2fd; padding:10px; border-radius:5px;"><strong>Când folosești:</strong> Volume mari de date, nevoie de 99.99% uptime, trafic global</p>
                        </div>
                    </div>
                    
                    <h4>Exemplu Practic (E-commerce):</h4>
                    <table style="width:100%; border-collapse:collapse;">
                        <tr style="background:#f5f5f5;">
                            <th style="border:1px solid #ddd; padding:10px;">Situație</th>
                            <th style="border:1px solid #ddd; padding:10px;">Soluție Recomandată</th>
                        </tr>
                        <tr>
                            <td style="border:1px solid #ddd; padding:10px;">10.000 produse, 100 comenzi/zi</td>
                            <td style="border:1px solid #ddd; padding:10px;"><strong>Vertical</strong> - un singur server e suficient</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid #ddd; padding:10px;">1M produse, 10.000 comenzi/zi</td>
                            <td style="border:1px solid #ddd; padding:10px;"><strong>Vertical + Replica Set</strong> - read scaling + HA</td>
                        </tr>
                        <tr>
                            <td style="border:1px solid #ddd; padding:10px;">100M produse, 1M comenzi/zi</td>
                            <td style="border:1px solid #ddd; padding:10px;"><strong>Horizontal (Sharding)</strong> - distribuție date obligatorie</td>
                        </tr>
                    </table>
                </div>
            `;
        }
    </script>
</body>
</html>
"""


def migrate_user_addresses():
    """
    Migreaza utilizatorii vechi de la address (singular) la addresses (array)
    """
    try:
        if db is None:
            return
        
        users_to_migrate = db.users.find({
            "address": {"$exists": True},
            "addresses": {"$exists": False}
        })
        
        for user in users_to_migrate:
            old_address = user.get('address', {})
            new_addresses = [{
                "label": "Acasa",
                "city": old_address.get('city', ''),
                "street": old_address.get('street', ''),
                "zip": old_address.get('zip', '')
            }]
            
            db.users.update_one(
                {"_id": user['_id']},
                {
                    "$set": {"addresses": new_addresses},
                    "$unset": {"address": ""}
                }
            )
        
        db.users.update_many(
            {"address": {"$exists": True}},
            {"$unset": {"address": ""}}
        )
        
        print("Migrare adrese completata!")
    except Exception as e:
        print(f"Eroare la migrare: {e}")

migrate_user_addresses()

@app.route('/')
def index():
    return render_template_string(HTML_INTERFACE)

@app.route('/api/stats')
def get_stats():
    """
    Folosim Aggregation Pipeline pentru a calcula statistici în baza de date,
    nu în Python. Acest lucru este mult mai eficient pentru dataset-uri mari.
    """
    try:
        total_products = db.products.count_documents({})
        
        total_orders = db.orders.count_documents({})
        
        revenue_pipeline = [
            {"$group": {"_id": None, "total": {"$sum": "$price_snapshot"}}}
        ]
        revenue_result = list(db.orders.aggregate(revenue_pipeline))
        total_revenue = revenue_result[0]["total"] if revenue_result else 0
        
        avg_pipeline = [
            {"$group": {"_id": None, "avg": {"$avg": "$price"}}}
        ]
        avg_result = list(db.products.aggregate(avg_pipeline))
        avg_price = round(avg_result[0]["avg"], 0) if avg_result else 0
        
        return jsonify({
            "total_products": total_products,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "avg_price": avg_price
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/products')
def get_products():
    """
    CRUD: READ - Citim produsele din MongoDB
    Folosim projection pentru a exclude _id (nu e serializabil în JSON direct)
    """
    try:
        prods = list(db.products.find({}, {'_id': 0}).limit(50))
        return jsonify(prods)
    except Exception as e:
        return jsonify({"error": "Eroare la citirea produselor", "details": str(e)}), 500

@app.route('/api/init', methods=['POST'])
def init_db_route():
    """
    CRUD: DELETE + CREATE
    Ștergem colecțiile existente și generăm date noi
    Demonstrează Flexible Schema - specs diferite per produs
    """
    try:
        db.products.drop()
        db.orders.drop()
        db.users.drop()
        
        products = []
        brands = ["Yamaha", "Honda", "Ducati", "BMW", "KTM", "Kawasaki", "Harley-Davidson"]
        types = ["Sport", "Naked", "Adventure", "Cruiser", "Enduro"]
        colors = ["Red", "Black", "Blue", "White", "Matte Black", "Orange"]
        
        for i in range(30):
            brand = random.choice(brands)
            moto_type = random.choice(types)
            cc = random.choice([300, 600, 750, 1000, 1200])
            
            products.append({
                "moto_id": f"M{i+100}",
                "name": f"{brand} {moto_type} {cc}",
                "brand": brand,  # Adăugăm brand separat pentru aggregation
                "type": moto_type,
                "cc": cc,
                "price": 5000 + (cc * 8) + random.randint(-500, 2000),
                "stock": random.randint(0, 8),
                "color": random.choice(colors),
                "specs": {
                    "weight_kg": random.randint(150, 280),
                    "fuel_tank_l": random.randint(12, 25),
                    "warranty_years": random.choice([1, 2, 3])
                },
                "vector_embedding": np.random.rand(5).tolist(),
                "created_at": datetime.now()
            })
        
        db.products.insert_many(products)
        
        users = []
        cities = ["Bucuresti", "Cluj-Napoca", "Timisoara", "Iasi", "Constanta"]
        streets = ["Str. Libertatii", "Bd. Unirii", "Calea Victoriei", "Str. Mihai Eminescu", "Aleea Rozelor"]
        labels = ["Acasa", "Birou", "Parinti"]
        
        for i in range(5):
            num_addresses = random.randint(1, 3)
            addresses = []
            for j in range(num_addresses):
                addresses.append({
                    "label": labels[j],
                    "city": random.choice(cities),
                    "street": f"{random.choice(streets)} {random.randint(1, 100)}",
                    "zip": f"{random.randint(100000, 999999)}"
                })
            
            users.append({
                "user_id": f"U{i+1}",
                "name": f"Client {i+1}",
                "email": f"client{i+1}@motoshop.ro",
                "addresses": addresses,
                "created_at": datetime.now()
            })
        db.users.insert_many(users)
        
        db.products.create_index("price")
        db.products.create_index("brand")
        db.products.create_index("moto_id")
        
        return jsonify({
            "status": "ok", 
            "products_count": len(products),
            "users_count": len(users)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/buy', methods=['POST'])
def buy_route():
    """
    CRUD: UPDATE (stoc) + CREATE (comandă)
    Folosim SNAPSHOT PATTERN - copiem prețul la momentul comenzii
    Folosim REFERENCING - customer_ref către user
    """
    try:
        data = request.json
        moto_id = data.get('id')
        
        if not moto_id:
            return jsonify({"success": False, "message": "ID produs lipsă!"})
        
        prod = db.products.find_one({"moto_id": moto_id})
        
        if not prod:
            return jsonify({"success": False, "message": "Produs inexistent!"})
        
        if prod['stock'] <= 0:
            return jsonify({"success": False, "message": "Stoc epuizat!"})
        
        result = db.products.update_one(
            {"moto_id": moto_id, "stock": {"$gt": 0}},  # Verificare atomică
            {"$inc": {"stock": -1}}
        )
        
        if result.modified_count == 0:
            return jsonify({"success": False, "message": "Eroare la actualizarea stocului!"})
        
        order = {
            "order_code": f"ORD-{random.randint(10000, 99999)}",
            "moto_id": moto_id,
            "product_name": prod['name'],  # SNAPSHOT
            "price_snapshot": prod['price'],  # SNAPSHOT - prețul nu se schimbă
            "date": datetime.now(),
            "status": "Confirmed"
        }
        db.orders.insert_one(order)
        
        return jsonify({
            "success": True, 
            "message": f"✅ Ai cumpărat {prod['name']} cu {prod['price']} €!"
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Eroare: {str(e)}"})

@app.route('/api/vector-search')
def search_route():
    """
    Simulare Vector Database Search
    În producție, s-ar folosi MongoDB Atlas Vector Search sau Pinecone
    Calculăm Cosine Similarity între vectori
    """
    try:
        query = np.random.rand(5)
        
        products = list(db.products.find({}, {'_id': 0}))
        results = []
        
        for p in products:
            if 'vector_embedding' in p:
                v = np.array(p['vector_embedding'])
                score = np.dot(query, v) / (np.linalg.norm(query) * np.linalg.norm(v))
                results.append({
                    "name": p['name'], 
                    "price": p['price'], 
                    "score": round(score * 100, 1)
                })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return jsonify(results[:5])  # Top 5 rezultate
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/test-performance')
def test_performance():
    """
    SCALING STRATEGY: Indexare
    Comparăm query cu și fără index pentru a demonstra impactul
    """
    try:
        query = {"price": {"$gt": 8000}}
        
        db.products.drop_indexes()
        start = time.time()
        count1 = db.products.count_documents(query)
        list(db.products.find(query))
        time1 = round((time.time() - start) * 1000, 2)  # ms
        
        db.products.create_index("price")
        start = time.time()
        count2 = db.products.count_documents(query)
        list(db.products.find(query))
        time2 = round((time.time() - start) * 1000, 2)  # ms
        
        improvement = round(time1 / time2, 1) if time2 > 0 else 1
        
        return jsonify({
            "without_index": {"time": time1, "count": count1},
            "with_index": {"time": time2, "count": count2},
            "improvement": improvement
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/aggregation')
def aggregation_pipeline():
    """
    AGGREGATION PIPELINE - Demonstrează capabilitățile MongoDB
    Pipeline: $match → $group → $sort → $project
    
    Echivalent SQL:
    SELECT brand, COUNT(*) as total, AVG(price) as avg_price, SUM(stock) as total_stock
    FROM products
    GROUP BY brand
    ORDER BY total DESC
    """
    try:
        pipeline = [
            {
                "$group": {
                    "_id": "$brand",
                    "total_products": {"$sum": 1},
                    "avg_price": {"$avg": "$price"},
                    "total_stock": {"$sum": "$stock"},
                    "min_price": {"$min": "$price"},
                    "max_price": {"$max": "$price"}
                }
            },
            {"$sort": {"total_products": -1}},
            {
                "$project": {
                    "_id": 1,
                    "total_products": 1,
                    "avg_price": {"$round": ["$avg_price", 0]},
                    "total_stock": 1,
                    "price_range": {
                        "$concat": [
                            {"$toString": "$min_price"},
                            " - ",
                            {"$toString": "$max_price"},
                            " €"
                        ]
                    }
                }
            }
        ]
        
        results = list(db.products.aggregate(pipeline))
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sharding-simulation')
def sharding_simulation():
    """
    SHARDING SIMULATION - Demonstrează cum ar fi distribuite datele pe shards
    
    În producție, sharding-ul este gestionat de MongoDB:
    - mongos (router) direcționează query-urile
    - config servers stochează metadata
    - shards conțin datele distribuite
    
    Aici simulăm distribuția folosind shard key: brand
    """
    try:
        products = list(db.products.find({}, {"brand": 1, "_id": 0}))
        
        all_brands = list(set(p.get('brand', 'Unknown') for p in products))
        all_brands.sort()
        
        shard_assignments = {}
        for i, brand in enumerate(all_brands):
            shard_num = i % 3
            shard_name = f"Shard {shard_num + 1}"
            if shard_name not in shard_assignments:
                shard_assignments[shard_name] = []
            shard_assignments[shard_name].append(brand)
        
        shards_info = []
        for shard_name, brands in shard_assignments.items():
            product_count = sum(1 for p in products if p.get('brand') in brands)
            shards_info.append({
                "name": shard_name,
                "brands": brands,
                "products": product_count
            })
        
        return jsonify({
            "total_products": len(products),
            "total_brands": len(all_brands),
            "shards": sorted(shards_info, key=lambda x: x['name'])
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users')
def get_users():
    """
    CRUD: READ - Citim utilizatorii din MongoDB
    Demonstrează EMBEDDING pattern - adresa este stocată în document
    """
    try:
        users = list(db.users.find({}, {'_id': 0}))
        return jsonify(users)
    except Exception as e:
        return jsonify([])

@app.route('/api/users', methods=['POST'])
def create_user():
    """
    CRUD: CREATE - Adaugam un utilizator nou in MongoDB
    Folosim EMBEDDING pattern pentru adrese (1:N limitat - max 3 adrese)
    
    ERROR HANDLING: Validam datele primite si returnam erori specifice
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "success": False,
                "message": "Eroare: Nu s-au primit date JSON valide!"
            }), 400
        
        if not data.get('name') or not data.get('name').strip():
            return jsonify({
                "success": False,
                "message": "Eroare: Numele este obligatoriu!"
            }), 400
            
        if not data.get('email') or not data.get('email').strip():
            return jsonify({
                "success": False,
                "message": "Eroare: Email-ul este obligatoriu!"
            }), 400
        
        email = data['email'].strip()
        if '@' not in email or '.' not in email.split('@')[-1]:
            return jsonify({
                "success": False,
                "message": "Eroare: Format email invalid!"
            }), 400
        
        existing_email = db.users.find_one({"email": email})
        if existing_email:
            return jsonify({
                "success": False,
                "message": f"Eroare: Email-ul {email} este deja folosit!"
            }), 400
        
        last_user = db.users.find_one(sort=[("user_id", -1)])
        if last_user:
            last_num = int(last_user['user_id'].replace('U', ''))
            new_id = f"U{last_num + 1}"
        else:
            new_id = "U1"
        
        addresses = data.get('addresses', [])
        if len(addresses) > 3:
            addresses = addresses[:3]  # Limitam la 3 adrese
        
        new_user = {
            "user_id": new_id,
            "name": data['name'].strip(),
            "email": email,
            "addresses": addresses,  # Array de adrese embedded
            "created_at": datetime.now()
        }
        
        db.users.insert_one(new_user)
        
        return jsonify({
            "success": True,
            "message": f"Utilizator {data['name']} adaugat cu succes!",
            "user_id": new_id
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Eroare: {str(e)}"})

@app.route('/api/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """
    CRUD: UPDATE - Modificam un utilizator existent
    Demonstreaza update pe array de adrese embedded
    """
    try:
        data = request.json
        
        existing_user = db.users.find_one({"user_id": user_id})
        if not existing_user:
            return jsonify({
                "success": False,
                "message": f"Utilizatorul {user_id} nu a fost gasit!"
            })
        
        addresses = data.get('addresses', [])
        if len(addresses) > 3:
            addresses = addresses[:3]
        
        result = db.users.update_one(
            {"user_id": user_id},
            {"$set": {
                "name": data['name'],
                "email": data['email'],
                "addresses": addresses,
                "updated_at": datetime.now()
            }}
        )
        
        return jsonify({
            "success": True,
            "message": f"Utilizator {user_id} actualizat cu succes!"
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Eroare: {str(e)}"})

@app.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    CRUD: DELETE - Stergem un utilizator din MongoDB
    """
    try:
        result = db.users.delete_one({"user_id": user_id})
        
        if result.deleted_count > 0:
            return jsonify({
                "success": True,
                "message": f"Utilizator {user_id} sters!"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Utilizatorul nu a fost gasit!"
            })
    except Exception as e:
        return jsonify({"success": False, "message": f"Eroare: {str(e)}"})

@app.route('/api/orders')
def get_orders():
    """
    CRUD: READ - Citim comenzile din MongoDB
    Demonstrează SNAPSHOT pattern - prețul este salvat la momentul comenzii
    """
    try:
        orders = list(db.orders.find({}, {'_id': 0}).sort('date', -1).limit(10))
        return jsonify(orders)
    except Exception as e:
        return jsonify([])

@app.route('/api/top-sales')
def top_sales():
    """
    Aggregation Pipeline pentru a găsi cele mai vândute produse
    Folosește $lookup pentru a face JOIN între orders și products
    """
    try:
        pipeline = [
            {
                "$group": {
                    "_id": "$moto_id",
                    "times_sold": {"$sum": 1},
                    "total_revenue": {"$sum": "$price_snapshot"}
                }
            },
            {"$sort": {"times_sold": -1}},
            {"$limit": 5}
        ]
        
        results = list(db.orders.aggregate(pipeline))
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/monthly-stats')
def monthly_stats():
    """
    Aggregation pentru statistici pe perioade de timp
    Grupare după an-lună
    """
    try:
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$date"},
                        "month": {"$month": "$date"}
                    },
                    "orders_count": {"$sum": 1},
                    "revenue": {"$sum": "$price_snapshot"}
                }
            },
            {"$sort": {"_id.year": -1, "_id.month": -1}}
        ]
        
        results = list(db.orders.aggregate(pipeline))
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🌍 Serverul Web pornește...")
    print("👉 Deschide browserul la adresa: http://127.0.0.1:5000")
    app.run(port=5000)