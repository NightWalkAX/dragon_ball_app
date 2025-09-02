// Dragon Ball Dashboard JavaScript

// Check if the page exists before trying to assign on_page_load
if (frappe.pages && frappe.pages['dragon-ball-dashboard']) {
    frappe.pages['dragon-ball-dashboard'].on_page_load = function(wrapper) {
        var page = frappe.ui.make_app_page({
            parent: wrapper,
            title: 'Dragon Ball Dashboard',
            single_column: true
        });

    // Add sync buttons
    page.add_action_item(__('Sync All Characters'), function() {
        sync_all_characters();
    });

    page.add_action_item(__('Refresh Dashboard'), function() {
        load_dashboard_data();
    });

    // Initialize dashboard
    load_dashboard_data();
    setup_search();
};

function sync_all_characters() {
    frappe.show_alert({
        message: __('Syncing characters from Dragon Ball API...'),
        indicator: 'blue'
    });

    frappe.call({
        method: 'dragon_ball_app.db_app.api.dragon_ball_api.sync_all_characters',
        callback: function(r) {
            if (r.message && r.message.status === 'success') {
                frappe.show_alert({
                    message: __('Successfully synced characters!'),
                    indicator: 'green'
                });
                load_dashboard_data(); // Refresh dashboard
            }
        },
        error: function(r) {
            frappe.show_alert({
                message: __('Error syncing characters'),
                indicator: 'red'
            });
        }
    });
}

function sync_single_character(character_id) {
    frappe.call({
        method: 'dragon_ball_app.db_app.api.dragon_ball_api.sync_single_character',
        args: {
            character_id: character_id
        },
        callback: function(r) {
            if (r.message && r.message.status === 'success') {
                frappe.show_alert({
                    message: __('Character synced successfully!'),
                    indicator: 'green'
                });
                load_dashboard_data(); // Refresh dashboard
            }
        },
        error: function(r) {
            frappe.show_alert({
                message: __('Error syncing character'),
                indicator: 'red'
            });
        }
    });
}

function load_dashboard_data() {
    frappe.call({
        method: 'dragon_ball_app.db_app.dashboard.dashboard.get_dashboard_data',
        callback: function(r) {
            if (r.message) {
                render_dashboard(r.message);
            }
        }
    });
}

function render_dashboard(data) {
    var dashboard_html = `
        <div class="row">
            <div class="col-sm-12">
                <h3>Dragon Ball Characters Dashboard</h3>
            </div>
        </div>
        
        <div class="row">
            <div class="col-sm-3">
                <div class="card">
                    <div class="card-body text-center">
                        <h2 class="text-primary">${data.total_characters}</h2>
                        <p>Total Characters</p>
                    </div>
                </div>
            </div>
            <div class="col-sm-4">
                <div class="card">
                    <div class="card-header">
                        <h5>Characters by Race</h5>
                    </div>
                    <div class="card-body">
                        ${render_race_distribution(data.race_distribution)}
                    </div>
                </div>
            </div>
            <div class="col-sm-5">
                <div class="card">
                    <div class="card-header">
                        <h5>Top Ki Characters</h5>
                    </div>
                    <div class="card-body">
                        ${render_top_characters(data.top_ki_characters)}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-sm-12">
                <div class="card">
                    <div class="card-header">
                        <h5>Recent Characters</h5>
                    </div>
                    <div class="card-body">
                        ${render_recent_characters(data.recent_characters)}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-sm-12">
                <div class="card">
                    <div class="card-header">
                        <h5>Search Characters</h5>
                    </div>
                    <div class="card-body">
                        <input type="text" id="character-search" class="form-control" placeholder="Search by name or race...">
                        <div id="search-results" class="mt-3"></div>
                    </div>
                </div>
            </div>
        </div>
    `;

    $('[data-page-route="dragon-ball-dashboard"] .page-content').html(dashboard_html);
}

function render_race_distribution(race_data) {
    if (!race_data || race_data.length === 0) {
        return '<p>No race data available</p>';
    }
    
    var html = '<ul class="list-group">';
    race_data.forEach(function(item) {
        html += `<li class="list-group-item d-flex justify-content-between align-items-center">
            ${item.race}
            <span class="badge badge-primary badge-pill">${item.count}</span>
        </li>`;
    });
    html += '</ul>';
    return html;
}

function render_top_characters(characters) {
    if (!characters || characters.length === 0) {
        return '<p>No character data available</p>';
    }
    
    var html = '<div class="list-group">';
    characters.forEach(function(char) {
        html += `<div class="list-group-item">
            <div class="d-flex w-100 justify-content-between">
                <h6 class="mb-1">${char.character_name}</h6>
                <small>Ki: ${char.ki}</small>
            </div>
            <p class="mb-1">Race: ${char.race}</p>
            <small>Max Ki: ${char.max_ki}</small>
        </div>`;
    });
    html += '</div>';
    return html;
}

function render_recent_characters(characters) {
    if (!characters || characters.length === 0) {
        return '<p>No recent characters</p>';
    }
    
    var html = '<div class="row">';
    characters.forEach(function(char) {
        html += `<div class="col-sm-6 col-md-4 mb-3">
            <div class="card">
                ${char.image_url ? `<img src="${char.image_url}" class="card-img-top" style="height: 200px; object-fit: cover;">` : ''}
                <div class="card-body">
                    <h6 class="card-title">${char.character_name}</h6>
                    <p class="card-text">
                        <small>Race: ${char.race || 'Unknown'}</small><br>
                        <small>Gender: ${char.gender || 'Unknown'}</small>
                    </p>
                </div>
            </div>
        </div>`;
    });
    html += '</div>';
    return html;
}

function setup_search() {
    $(document).on('input', '#character-search', function() {
        var search_term = $(this).val();
        if (search_term.length > 2) {
            search_characters(search_term);
        } else {
            $('#search-results').html('');
        }
    });
}

function search_characters(search_term) {
    frappe.call({
        method: 'dragon_ball_app.db_app.dashboard.dashboard.search_characters',
        args: {
            search_term: search_term
        },
        callback: function(r) {
            if (r.message) {
                render_search_results(r.message);
            }
        }
    });
}

function render_search_results(characters) {
    if (!characters || characters.length === 0) {
        $('#search-results').html('<p>No characters found</p>');
        return;
    }
    
    var html = '<div class="list-group">';
    characters.forEach(function(char) {
        html += `<div class="list-group-item list-group-item-action" onclick="view_character('${char.name}')">
            <div class="d-flex w-100 justify-content-between">
                <h6 class="mb-1">${char.character_name}</h6>
                <small>Ki: ${char.ki || 'Unknown'}</small>
            </div>
            <p class="mb-1">Race: ${char.race || 'Unknown'} | Gender: ${char.gender || 'Unknown'}</p>
        </div>`;
    });
    html += '</div>';
    
    $('#search-results').html(html);
}

function view_character(character_name) {
    frappe.set_route('Form', 'Dragon Ball Character', character_name);
}

// Close the conditional block for page existence check
}
