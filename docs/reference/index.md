# API coverage

All **324** endpoints of the [iikoCloud API](https://api-ru.iiko.services/docs) that are not superseded by a newer version.
The attribute path of each method mirrors the endpoint URL. *Commands* return a `correlation_id`;
see [Asynchronous commands](../guide/commands.md).

Deprecated endpoints replaced by a newer version are not exposed: `/api/1/access_token`, `/api/2/menu/by_id`, `/api/nomenclature/v1/assembly-chart/create`, `/api/nomenclature/v1/assembly-chart/delete`, `/api/nomenclature/v1/assembly-chart/get`, `/api/nomenclature/v1/assembly-chart/list`, `/api/nomenclature/v1/assembly-chart/update`, `/api/nomenclature/v1/group/create`, `/api/nomenclature/v1/group/delete`, `/api/nomenclature/v1/group/list`, `/api/nomenclature/v1/group/restore`, `/api/nomenclature/v1/group/update`, `/api/nomenclature/v1/product/create`, `/api/nomenclature/v1/product/delete`, `/api/nomenclature/v1/product/list`, `/api/nomenclature/v1/product/restore`, `/api/nomenclature/v1/product/update`, `/api/nomenclature/v1/product/update_barcodes`. `/api/1/access_token` is still supported through `ApiLoginAuth`.

## [General](general.md)

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/v2/access_token` | [`iiko.access_token()`](general.md#iikocloudapi.resources.IikoCloudResources.access_token) | Retrieve session key for API access (v2) |
| `/api/1/notifications/send` | [`iiko.notifications.send()`](general.md#iikocloudapi.resources.notifications.NotificationsResource.send) | Send notification to external systems |
| `/api/1/organizations` | [`iiko.organizations()`](general.md#iikocloudapi.resources.organizations.OrganizationsResource.__call__) | Returns organizations available to api-login user |
| `/api/1/organizations/settings` | [`iiko.organizations.settings()`](general.md#iikocloudapi.resources.organizations.OrganizationsResource.settings) | Returns available to api-login user organizations specified settings |
| `/api/1/terminal_groups` | [`iiko.terminal_groups()`](general.md#iikocloudapi.resources.terminal_groups.TerminalGroupsResource.__call__) | Method that returns information on groups of delivery terminals |
| `/api/1/terminal_groups/awake` | [`iiko.terminal_groups.awake()`](general.md#iikocloudapi.resources.terminal_groups.TerminalGroupsResource.awake) | Awake terminal groups from sleep mode |
| `/api/1/terminal_groups/is_alive` | [`iiko.terminal_groups.is_alive()`](general.md#iikocloudapi.resources.terminal_groups.TerminalGroupsResource.is_alive) | Returns information on availability of group of terminals |
| `/api/1/cancel_causes` | [`iiko.cancel_causes()`](general.md#iikocloudapi.resources.IikoCloudResources.cancel_causes) | Delivery cancel causes |
| `/api/1/deliveries/order_types` | [`iiko.deliveries.order_types()`](general.md#iikocloudapi.resources.deliveries.DeliveriesResource.order_types) | Order types |
| `/api/1/discounts` | [`iiko.discounts()`](general.md#iikocloudapi.resources.IikoCloudResources.discounts) | Discounts / surcharges |
| `/api/1/payment_types` | [`iiko.payment_types()`](general.md#iikocloudapi.resources.IikoCloudResources.payment_types) | Payment types |
| `/api/1/removal_types` | [`iiko.removal_types()`](general.md#iikocloudapi.resources.IikoCloudResources.removal_types) | Removal types (reasons for deletion) |
| `/api/1/tips_types` | [`iiko.tips_types()`](general.md#iikocloudapi.resources.IikoCloudResources.tips_types) | Get tips types for api-login`s rms group |
| `/api/1/combo` | [`iiko.combo()`](general.md#iikocloudapi.resources.combo.ComboResource.__call__) | Get combos info |
| `/api/1/combo/calculate` | [`iiko.combo.calculate()`](general.md#iikocloudapi.resources.combo.ComboResource.calculate) | Calculate combo price |
| `/api/2/menu` | [`iiko.menu()`](general.md#iikocloudapi.resources.menu.MenuResource.__call__) | External menus with price categories |
| `/api/menu/v3/by_id` | [`iiko.menu.by_id()`](general.md#iikocloudapi.resources.menu.MenuResource.by_id) | Retrieve external menu V3 by ID |
| `/api/1/nomenclature` | [`iiko.nomenclature()`](general.md#iikocloudapi.resources.nomenclature.NomenclatureResource.__call__) | Menu *(deprecated)* |
| `/api/1/stop_lists` | [`iiko.stop_lists()`](general.md#iikocloudapi.resources.stop_lists.StopListsResource.__call__) | Out-of-stock items |
| `/api/1/stop_lists/add` | [`iiko.stop_lists.add()`](general.md#iikocloudapi.resources.stop_lists.StopListsResource.add) | Add items to out-of-stock list.
 (You should have extra rights to use this method) |
| `/api/1/stop_lists/check` | [`iiko.stop_lists.check()`](general.md#iikocloudapi.resources.stop_lists.StopListsResource.check) | Check items in out-of-stock list |
| `/api/1/stop_lists/clear` | [`iiko.stop_lists.clear()`](general.md#iikocloudapi.resources.stop_lists.StopListsResource.clear) | Clear out-of-stock list.
 (You should have extra rights to use this method) |
| `/api/1/stop_lists/remove` | [`iiko.stop_lists.remove()`](general.md#iikocloudapi.resources.stop_lists.StopListsResource.remove) | Remove items from out-of-stock list.
 (You should have extra rights to use this method) |
| `/api/1/commands/status` | [`iiko.commands.status()`](general.md#iikocloudapi.resources.commands.CommandsResource.status) | Get status of command |
| `/api/1/employees/couriers` | [`iiko.employees.couriers()`](general.md#iikocloudapi.resources.employees.EmployeesCouriersResource.__call__) | Returns list of all employees which are delivery drivers in specified restaurants |
| `/api/1/employees/couriers/active_location` | [`iiko.employees.couriers.active_location()`](general.md#iikocloudapi.resources.employees.EmployeesCouriersActiveLocationResource.__call__) | Returns list of all active (courier session is opened) courier's locations which are delivery drivers 
 in specified restaurants |
| `/api/1/employees/couriers/active_location/by_terminal` | [`iiko.employees.couriers.active_location.by_terminal()`](general.md#iikocloudapi.resources.employees.EmployeesCouriersActiveLocationResource.by_terminal) | Returns list of all active (courier session is opened) courier's locations which are delivery drivers in specified 
 restaurant and are clocked in on specified delivery terminal |
| `/api/1/employees/couriers/by_role` | [`iiko.employees.couriers.by_role()`](general.md#iikocloudapi.resources.employees.EmployeesCouriersResource.by_role) | Returns list of all employees which are delivery drivers in specified restaurants, 
 and checks whether each employee has passed role |
| `/api/1/employees/couriers/locations/by_time_offset` | [`iiko.employees.couriers.locations.by_time_offset()`](general.md#iikocloudapi.resources.employees.EmployeesCouriersLocationsResource.by_time_offset) | Method of obtaining drivers' coordinates history |
| `/api/1/employees/info` | [`iiko.employees.info()`](general.md#iikocloudapi.resources.employees.EmployeesResource.info) | Returns employee info |
| `/api/1/employees/shift/clockin` | [`iiko.employees.shift.clockin()`](general.md#iikocloudapi.resources.employees.EmployeesShiftResource.clockin) | Open personal session *(command)* |
| `/api/1/employees/shift/clockout` | [`iiko.employees.shift.clockout()`](general.md#iikocloudapi.resources.employees.EmployeesShiftResource.clockout) | Close personal session *(command)* |
| `/api/1/employees/shift/is_open` | [`iiko.employees.shift.is_open()`](general.md#iikocloudapi.resources.employees.EmployeesShiftResource.is_open) | Check if personal session is open |
| `/api/1/employees/shifts/by_courier` | [`iiko.employees.shifts.by_courier()`](general.md#iikocloudapi.resources.employees.EmployeesShiftsResource.by_courier) | Get terminal groups where employee session is opened |

## [Delivery](delivery.md)

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/1/deliveries/add_items` | [`iiko.deliveries.add_items()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesResource.add_items) | Add order items *(command)* |
| `/api/1/deliveries/add_payments` | [`iiko.deliveries.add_payments()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesResource.add_payments) | Add order payments *(command)* |
| `/api/1/deliveries/cancel` | [`iiko.deliveries.cancel()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesResource.cancel) | Cancel delivery order *(command)* |
| `/api/1/deliveries/cancel_confirmation` | [`iiko.deliveries.cancel_confirmation()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesResource.cancel_confirmation) | Cancel delivery confirmation *(command)* |
| `/api/1/deliveries/change_comment` | [`iiko.deliveries.change_comment()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesResource.change_comment) | Change delivery comment *(command)* |
| `/api/1/deliveries/change_complete_before` | [`iiko.deliveries.change_complete_before()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesResource.change_complete_before) | Change time when client wants the order to be delivered *(command)* |
| `/api/1/deliveries/change_delivery_point` | [`iiko.deliveries.change_delivery_point()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesResource.change_delivery_point) | Change order's delivery point information *(command)* |
| `/api/1/deliveries/change_driver_info` | [`iiko.deliveries.change_driver_info()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesResource.change_driver_info) | Change driver info *(command)* |
| `/api/1/deliveries/change_external_data` | [`iiko.deliveries.change_external_data()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesResource.change_external_data) | Change delivery external data |
| `/api/1/deliveries/change_operator` | [`iiko.deliveries.change_operator()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesResource.change_operator) | Assign/change the order operator *(command)* |
| `/api/1/deliveries/change_payments` | [`iiko.deliveries.change_payments()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesResource.change_payments) | Change order's payments *(command)* |
| `/api/1/deliveries/change_service_type` | [`iiko.deliveries.change_service_type()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesResource.change_service_type) | Change order's delivery type *(command)* |
| `/api/1/deliveries/close` | [`iiko.deliveries.close()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesResource.close) | Close order *(command)* |
| `/api/1/deliveries/confirm` | [`iiko.deliveries.confirm()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesResource.confirm) | Confirm delivery *(command)* |
| `/api/1/deliveries/create` | [`iiko.deliveries.create()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesResource.create) | Create delivery *(command)* |
| `/api/1/deliveries/print_delivery_bill` | [`iiko.deliveries.print_delivery_bill()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesResource.print_delivery_bill) | Print delivery bill *(command)* |
| `/api/1/deliveries/update_order_courier` | [`iiko.deliveries.update_order_courier()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesResource.update_order_courier) | Update order courier *(deprecated)* *(command)* |
| `/api/1/deliveries/update_order_delivery_status` | [`iiko.deliveries.update_order_delivery_status()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesResource.update_order_delivery_status) | Update delivery status *(command)* |
| `/api/1/deliveries/update_order_payments` | [`iiko.deliveries.update_order_payments()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesResource.update_order_payments) | Update order payment details *(deprecated)* *(command)* |
| `/api/1/deliveries/update_order_problem` | [`iiko.deliveries.update_order_problem()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesResource.update_order_problem) | Update order problem *(command)* |
| `/api/1/deliveries/update_tracking_link` | [`iiko.deliveries.update_tracking_link()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesResource.update_tracking_link) | Update tracking link of an order |
| `/api/1/order/print_bill` | [`iiko.order.print_bill()`](delivery.md#iikocloudapi.resources.order.OrderResource.print_bill) | Print bill *(command)* |
| `/api/1/deliveries/by_delivery_date_and_phone` | [`iiko.deliveries.by_delivery_date_and_phone()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesResource.by_delivery_date_and_phone) | Retrieve list of orders by telephone number, dates and revision |
| `/api/1/deliveries/by_delivery_date_and_source_key_and_filter` | [`iiko.deliveries.by_delivery_date_and_source_key_and_filter()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesResource.by_delivery_date_and_source_key_and_filter) | Search orders by search text and additional filters (date, problem, statuses and other) |
| `/api/1/deliveries/by_delivery_date_and_status` | [`iiko.deliveries.by_delivery_date_and_status()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesResource.by_delivery_date_and_status) | Retrieve list of orders by statuses and dates |
| `/api/1/deliveries/by_id` | [`iiko.deliveries.by_id()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesResource.by_id) | Retrieve orders by IDs |
| `/api/1/deliveries/by_revision` | [`iiko.deliveries.by_revision()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesResource.by_revision) | Retrieve list of orders changed from the time revision was passed |
| `/api/1/deliveries/history/by_delivery_date_and_phone` | [`iiko.deliveries.history.by_delivery_date_and_phone()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesHistoryResource.by_delivery_date_and_phone) | Retrieve list of history orders by telephone number, dates and revision |
| `/api/1/cities` | [`iiko.cities()`](delivery.md#iikocloudapi.resources.IikoCloudResources.cities) | Cities |
| `/api/1/regions` | [`iiko.regions()`](delivery.md#iikocloudapi.resources.IikoCloudResources.regions) | Regions |
| `/api/1/streets/by_city` | [`iiko.streets.by_city()`](delivery.md#iikocloudapi.resources.streets.StreetsResource.by_city) | Streets by city |
| `/api/1/streets/by_id` | [`iiko.streets.by_id()`](delivery.md#iikocloudapi.resources.streets.StreetsResource.by_id) | Streets by id or by classifierId |
| `/api/1/delivery_restrictions` | [`iiko.delivery_restrictions()`](delivery.md#iikocloudapi.resources.delivery_restrictions.DeliveryRestrictionsResource.__call__) | Retrieve list of delivery restrictions |
| `/api/1/delivery_restrictions/allowed` | [`iiko.delivery_restrictions.allowed()`](delivery.md#iikocloudapi.resources.delivery_restrictions.DeliveryRestrictionsResource.allowed) | Get suitable terminal groups for delivery restrictions |
| `/api/1/marketing_sources` | [`iiko.marketing_sources()`](delivery.md#iikocloudapi.resources.IikoCloudResources.marketing_sources) | Marketing sources |
| `/api/1/deliveries/drafts/by_filter` | [`iiko.deliveries.drafts.by_filter()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesDraftsResource.by_filter) | Retrieve order drafts list by parameters |
| `/api/1/deliveries/drafts/by_id` | [`iiko.deliveries.drafts.by_id()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesDraftsResource.by_id) | Retrieve order draft by ID |
| `/api/1/deliveries/drafts/commit` | [`iiko.deliveries.drafts.commit()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesDraftsResource.commit) | Admit order draft changes and send them to Front |
| `/api/1/deliveries/drafts/create` | [`iiko.deliveries.drafts.create()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesDraftsResource.create) | Create delivery order draft |
| `/api/1/deliveries/drafts/delete` | [`iiko.deliveries.drafts.delete()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesDraftsResource.delete) | Delete order draft |
| `/api/1/deliveries/drafts/lock` | [`iiko.deliveries.drafts.lock()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesDraftsResource.lock) | Lock order draft |
| `/api/1/deliveries/drafts/save` | [`iiko.deliveries.drafts.save()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesDraftsResource.save) | Update existing delivery order draft |
| `/api/1/deliveries/drafts/unlock` | [`iiko.deliveries.drafts.unlock()`](delivery.md#iikocloudapi.resources.deliveries.DeliveriesDraftsResource.unlock) | Unlock order draft |

## [Orders](orders.md)

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/1/order/add_customer` | [`iiko.order.add_customer()`](orders.md#iikocloudapi.resources.order.OrderResource.add_customer) | Add customer to order *(command)* |
| `/api/1/order/add_items` | [`iiko.order.add_items()`](orders.md#iikocloudapi.resources.order.OrderResource.add_items) | Add order items *(command)* |
| `/api/1/order/add_payments` | [`iiko.order.add_payments()`](orders.md#iikocloudapi.resources.order.OrderResource.add_payments) | Add order payments *(command)* |
| `/api/1/order/by_id` | [`iiko.order.by_id()`](orders.md#iikocloudapi.resources.order.OrderResource.by_id) | Retrieve orders by IDs |
| `/api/1/order/by_table` | [`iiko.order.by_table()`](orders.md#iikocloudapi.resources.order.OrderResource.by_table) | Retrieve orders by tables |
| `/api/1/order/cancel` | [`iiko.order.cancel()`](orders.md#iikocloudapi.resources.order.OrderResource.cancel) | Cancel the table order *(command)* |
| `/api/1/order/change_external_data` | [`iiko.order.change_external_data()`](orders.md#iikocloudapi.resources.order.OrderResource.change_external_data) | Change table order external_data |
| `/api/1/order/change_payments` | [`iiko.order.change_payments()`](orders.md#iikocloudapi.resources.order.OrderResource.change_payments) | Change table order's payments |
| `/api/1/order/close` | [`iiko.order.close()`](orders.md#iikocloudapi.resources.order.OrderResource.close) | Close order *(command)* |
| `/api/1/order/create` | [`iiko.order.create()`](orders.md#iikocloudapi.resources.order.OrderResource.create) | Create order *(command)* |
| `/api/1/order/init_by_posOrder` | [`iiko.order.init_by_pos_order()`](orders.md#iikocloudapi.resources.order.OrderResource.init_by_pos_order) | Init orders, created on POS, by POS orders |
| `/api/1/order/init_by_table` | [`iiko.order.init_by_table()`](orders.md#iikocloudapi.resources.order.OrderResource.init_by_table) | Init orders, created on POS, by tables |

## [Reserves](reserves.md)

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/1/reserve/add_items` | [`iiko.reserve.add_items()`](reserves.md#iikocloudapi.resources.reserve.ReserveResource.add_items) | Add order items *(command)* |
| `/api/1/reserve/add_payments` | [`iiko.reserve.add_payments()`](reserves.md#iikocloudapi.resources.reserve.ReserveResource.add_payments) | Add order payments *(command)* |
| `/api/1/reserve/available_organizations` | [`iiko.reserve.available_organizations()`](reserves.md#iikocloudapi.resources.reserve.ReserveResource.available_organizations) | Returns all organizations of current account (determined by Authorization request header) for which banquet/reserve booking are available |
| `/api/1/reserve/available_restaurant_sections` | [`iiko.reserve.available_restaurant_sections()`](reserves.md#iikocloudapi.resources.reserve.ReserveResource.available_restaurant_sections) | Returns all restaurant sections of specified terminal groups, for which banquet/reserve booking are available |
| `/api/1/reserve/available_terminal_groups` | [`iiko.reserve.available_terminal_groups()`](reserves.md#iikocloudapi.resources.reserve.ReserveResource.available_terminal_groups) | Returns all terminal groups of specified organizations, for which banquet/reserve booking are available |
| `/api/1/reserve/cancel` | [`iiko.reserve.cancel()`](reserves.md#iikocloudapi.resources.reserve.ReserveResource.cancel) | Cancel reservation due to some reason *(command)* |
| `/api/1/reserve/change_estimated_start_time` | [`iiko.reserve.change_estimated_start_time()`](reserves.md#iikocloudapi.resources.reserve.ReserveResource.change_estimated_start_time) | Change reserve/banquet estimated start time *(command)* |
| `/api/1/reserve/change_items` | [`iiko.reserve.change_items()`](reserves.md#iikocloudapi.resources.reserve.ReserveResource.change_items) | Change order items *(command)* |
| `/api/1/reserve/change_tables` | [`iiko.reserve.change_tables()`](reserves.md#iikocloudapi.resources.reserve.ReserveResource.change_tables) | Change reserve/banquet tables *(command)* |
| `/api/1/reserve/create` | [`iiko.reserve.create()`](reserves.md#iikocloudapi.resources.reserve.ReserveResource.create) | Create banquet/reserve *(command)* |
| `/api/1/reserve/restaurant_sections_workload` | [`iiko.reserve.restaurant_sections_workload()`](reserves.md#iikocloudapi.resources.reserve.ReserveResource.restaurant_sections_workload) | Returns all banquets/reserves for passed restaurant sections |
| `/api/1/reserve/status_by_id` | [`iiko.reserve.status_by_id()`](reserves.md#iikocloudapi.resources.reserve.ReserveResource.status_by_id) | Retrieve banquets/reserves statuses by IDs |

## [WebHooks](webhooks.md)

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/1/webhooks/settings` | [`iiko.webhooks.settings()`](webhooks.md#iikocloudapi.resources.webhooks.WebhooksResource.settings) | Get webhooks settings for specified organization and authorized API login |
| `/api/1/webhooks/update_settings` | [`iiko.webhooks.update_settings()`](webhooks.md#iikocloudapi.resources.webhooks.WebhooksResource.update_settings) | Update webhooks settings for specified organization and authorized API login |

## [Licenses](licenses.md)

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/licenses/v2/list` | [`iiko.licenses.list()`](licenses.md#iikocloudapi.resources.licenses.LicensesResource.list) | Get license list information for the API login |

## [Loyalty and discounts](loyalty-and-discounts.md)

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/1/loyalty/iiko/calculate` | [`iiko.loyalty.calculate()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyResource.calculate) | Calculate checkin |
| `/api/1/loyalty/iiko/coupons/by_series` | [`iiko.loyalty.coupons.by_series()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyCouponsResource.by_series) | Get non-activated coupons |
| `/api/1/loyalty/iiko/coupons/info` | [`iiko.loyalty.coupons.info()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyCouponsResource.info) | Get coupon info |
| `/api/1/loyalty/iiko/coupons/series` | [`iiko.loyalty.coupons.series()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyCouponsResource.series) | Get coupon series with non-activated coupons |
| `/api/1/loyalty/iiko/manual_condition` | [`iiko.loyalty.manual_condition()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyResource.manual_condition) | Get manual conditions |
| `/api/1/loyalty/iiko/program` | [`iiko.loyalty.program()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyResource.program) | Get programs |
| `/api/1/loyalty/iiko/customer_category` | [`iiko.loyalty.customer_category()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyCustomerCategoryResource.__call__) | Get customer categories |
| `/api/1/loyalty/iiko/customer_category/add` | [`iiko.loyalty.customer_category.add()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyCustomerCategoryResource.add) | Add category for customer |
| `/api/1/loyalty/iiko/customer_category/remove` | [`iiko.loyalty.customer_category.remove()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyCustomerCategoryResource.remove) | Remove category for customer |
| `/api/1/loyalty/iiko/customer/card/add` | [`iiko.loyalty.customer.card.add()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyCustomerCardResource.add) | Add card |
| `/api/1/loyalty/iiko/customer/card/remove` | [`iiko.loyalty.customer.card.remove()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyCustomerCardResource.remove) | Delete card |
| `/api/1/loyalty/iiko/customer/create_or_update` | [`iiko.loyalty.customer.create_or_update()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyCustomerResource.create_or_update) | Create or update customer |
| `/api/1/loyalty/iiko/customer/info` | [`iiko.loyalty.customer.info()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyCustomerResource.info) | Get customer info |
| `/api/1/loyalty/iiko/customer/program/add` | [`iiko.loyalty.customer.program.add()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyCustomerProgramResource.add) | Add customer to program |
| `/api/1/loyalty/iiko/customer/wallet/cancel_hold` | [`iiko.loyalty.customer.wallet.cancel_hold()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyCustomerWalletResource.cancel_hold) | Cancel hold money |
| `/api/1/loyalty/iiko/customer/wallet/chargeoff` | [`iiko.loyalty.customer.wallet.chargeoff()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyCustomerWalletResource.chargeoff) | Withdraw balance |
| `/api/1/loyalty/iiko/customer/wallet/hold` | [`iiko.loyalty.customer.wallet.hold()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyCustomerWalletResource.hold) | Hold money |
| `/api/1/loyalty/iiko/customer/wallet/topup` | [`iiko.loyalty.customer.wallet.topup()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyCustomerWalletResource.topup) | Refill balance |
| `/api/1/loyalty/iiko/delete_customers` | [`iiko.loyalty.delete_customers()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyResource.delete_customers) | Logical deletion of customers |
| `/api/1/loyalty/iiko/get_counters` | [`iiko.loyalty.get_counters()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyResource.get_counters) | Get counters |
| `/api/1/loyalty/iiko/restore_customers` | [`iiko.loyalty.restore_customers()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyResource.restore_customers) | Logical recovery of customers |
| `/api/1/loyalty/iiko/check_sms_sending_possibility` | [`iiko.loyalty.check_sms_sending_possibility()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyResource.check_sms_sending_possibility) | Check sms sending possibility |
| `/api/1/loyalty/iiko/check_sms_status` | [`iiko.loyalty.check_sms_status()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyResource.check_sms_status) | Check SMS status |
| `/api/1/loyalty/iiko/message/send_email` | [`iiko.loyalty.message.send_email()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyMessageResource.send_email) | Send email |
| `/api/1/loyalty/iiko/message/send_sms` | [`iiko.loyalty.message.send_sms()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyMessageResource.send_sms) | Send sms |
| `/api/1/loyalty/iiko/customer/transactions/by_date` | [`iiko.loyalty.customer.transactions.by_date()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyCustomerTransactionsResource.by_date) | Get transaction report by period |
| `/api/1/loyalty/iiko/customer/transactions/by_revision` | [`iiko.loyalty.customer.transactions.by_revision()`](loyalty-and-discounts.md#iikocloudapi.resources.loyalty.LoyaltyCustomerTransactionsResource.by_revision) | Get transaction report by revision |

## [Inventory](inventory.md)

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/inventory/v1/incoming_invoice/cancel` | [`iiko.inventory.incoming_invoice.cancel()`](inventory.md#iikocloudapi.resources.inventory.InventoryIncomingInvoiceResource.cancel) | Cancel incoming invoice draft |
| `/api/inventory/v1/incoming_invoice/create` | [`iiko.inventory.incoming_invoice.create()`](inventory.md#iikocloudapi.resources.inventory.InventoryIncomingInvoiceResource.create) | Create incoming invoice |
| `/api/inventory/v1/incoming_invoice/get` | [`iiko.inventory.incoming_invoice.get()`](inventory.md#iikocloudapi.resources.inventory.InventoryIncomingInvoiceResource.get) | Get incoming invoice by identifier |
| `/api/inventory/v1/incoming_invoice/list` | [`iiko.inventory.incoming_invoice.list()`](inventory.md#iikocloudapi.resources.inventory.InventoryIncomingInvoiceResource.list) | Export incoming invoices |
| `/api/inventory/v1/incoming_invoice/modify/add_payment` | [`iiko.inventory.incoming_invoice.modify.add_payment()`](inventory.md#iikocloudapi.resources.inventory.InventoryIncomingInvoiceModifyResource.add_payment) | Pay incoming invoice |
| `/api/inventory/v1/incoming_invoice/patch/set_payment_date` | [`iiko.inventory.incoming_invoice.patch.set_payment_date()`](inventory.md#iikocloudapi.resources.inventory.InventoryIncomingInvoicePatchResource.set_payment_date) | Set payment date for incoming invoice |
| `/api/inventory/v1/incoming_invoice/post` | [`iiko.inventory.incoming_invoice.post()`](inventory.md#iikocloudapi.resources.inventory.InventoryIncomingInvoiceResource.post) | Post incoming invoice |
| `/api/inventory/v1/incoming_invoice/unpost` | [`iiko.inventory.incoming_invoice.unpost()`](inventory.md#iikocloudapi.resources.inventory.InventoryIncomingInvoiceResource.unpost) | Unpost incoming invoice |
| `/api/inventory/v1/incoming_invoice/update` | [`iiko.inventory.incoming_invoice.update()`](inventory.md#iikocloudapi.resources.inventory.InventoryIncomingInvoiceResource.update) | Edit incoming invoice |
| `/api/inventory/v1/costings/calculate` | [`iiko.inventory.costings.calculate()`](inventory.md#iikocloudapi.resources.inventory.InventoryCostingsResource.calculate) | Get cost prices for nomenclature items |
| `/api/inventory/v1/outgoing_invoice/cancel` | [`iiko.inventory.outgoing_invoice.cancel()`](inventory.md#iikocloudapi.resources.inventory.InventoryOutgoingInvoiceResource.cancel) | Cancel outgoing invoice draft |
| `/api/inventory/v1/outgoing_invoice/create` | [`iiko.inventory.outgoing_invoice.create()`](inventory.md#iikocloudapi.resources.inventory.InventoryOutgoingInvoiceResource.create) | Create outgoing invoice |
| `/api/inventory/v1/outgoing_invoice/get` | [`iiko.inventory.outgoing_invoice.get()`](inventory.md#iikocloudapi.resources.inventory.InventoryOutgoingInvoiceResource.get) | Get outgoing invoice by ID |
| `/api/inventory/v1/outgoing_invoice/list` | [`iiko.inventory.outgoing_invoice.list()`](inventory.md#iikocloudapi.resources.inventory.InventoryOutgoingInvoiceResource.list) | Export outgoing invoices |
| `/api/inventory/v1/outgoing_invoice/modify/add_payment` | [`iiko.inventory.outgoing_invoice.modify.add_payment()`](inventory.md#iikocloudapi.resources.inventory.InventoryOutgoingInvoiceModifyResource.add_payment) | Pay outgoing invoice |
| `/api/inventory/v1/outgoing_invoice/patch/set_payment_date` | [`iiko.inventory.outgoing_invoice.patch.set_payment_date()`](inventory.md#iikocloudapi.resources.inventory.InventoryOutgoingInvoicePatchResource.set_payment_date) | Set payment date for outgoing invoice |
| `/api/inventory/v1/outgoing_invoice/post` | [`iiko.inventory.outgoing_invoice.post()`](inventory.md#iikocloudapi.resources.inventory.InventoryOutgoingInvoiceResource.post) | Post outgoing invoice |
| `/api/inventory/v1/outgoing_invoice/unpost` | [`iiko.inventory.outgoing_invoice.unpost()`](inventory.md#iikocloudapi.resources.inventory.InventoryOutgoingInvoiceResource.unpost) | Unpost outgoing invoice |
| `/api/inventory/v1/outgoing_invoice/update` | [`iiko.inventory.outgoing_invoice.update()`](inventory.md#iikocloudapi.resources.inventory.InventoryOutgoingInvoiceResource.update) | Edit outgoing invoice |
| `/api/inventory/v1/returned_invoice/cancel` | [`iiko.inventory.returned_invoice.cancel()`](inventory.md#iikocloudapi.resources.inventory.InventoryReturnedInvoiceResource.cancel) | Cancel returned invoice draft |
| `/api/inventory/v1/returned_invoice/create` | [`iiko.inventory.returned_invoice.create()`](inventory.md#iikocloudapi.resources.inventory.InventoryReturnedInvoiceResource.create) | Create returned invoice |
| `/api/inventory/v1/returned_invoice/get` | [`iiko.inventory.returned_invoice.get()`](inventory.md#iikocloudapi.resources.inventory.InventoryReturnedInvoiceResource.get) | Get returned invoice by identifier |
| `/api/inventory/v1/returned_invoice/list` | [`iiko.inventory.returned_invoice.list()`](inventory.md#iikocloudapi.resources.inventory.InventoryReturnedInvoiceResource.list) | Export returned invoices |
| `/api/inventory/v1/returned_invoice/post` | [`iiko.inventory.returned_invoice.post()`](inventory.md#iikocloudapi.resources.inventory.InventoryReturnedInvoiceResource.post) | Post returned invoice |
| `/api/inventory/v1/returned_invoice/unpost` | [`iiko.inventory.returned_invoice.unpost()`](inventory.md#iikocloudapi.resources.inventory.InventoryReturnedInvoiceResource.unpost) | Unpost returned invoice |
| `/api/inventory/v1/returned_invoice/update` | [`iiko.inventory.returned_invoice.update()`](inventory.md#iikocloudapi.resources.inventory.InventoryReturnedInvoiceResource.update) | Edit returned invoice |
| `/api/inventory/v1/incoming_returned_invoice/cancel` | [`iiko.inventory.incoming_returned_invoice.cancel()`](inventory.md#iikocloudapi.resources.inventory.InventoryIncomingReturnedInvoiceResource.cancel) | Cancel incoming returned invoice draft |
| `/api/inventory/v1/incoming_returned_invoice/create` | [`iiko.inventory.incoming_returned_invoice.create()`](inventory.md#iikocloudapi.resources.inventory.InventoryIncomingReturnedInvoiceResource.create) | Create incoming returned invoice |
| `/api/inventory/v1/incoming_returned_invoice/get` | [`iiko.inventory.incoming_returned_invoice.get()`](inventory.md#iikocloudapi.resources.inventory.InventoryIncomingReturnedInvoiceResource.get) | Get incoming returned invoice by identifier |
| `/api/inventory/v1/incoming_returned_invoice/list` | [`iiko.inventory.incoming_returned_invoice.list()`](inventory.md#iikocloudapi.resources.inventory.InventoryIncomingReturnedInvoiceResource.list) | Export incoming returned invoices |
| `/api/inventory/v1/incoming_returned_invoice/post` | [`iiko.inventory.incoming_returned_invoice.post()`](inventory.md#iikocloudapi.resources.inventory.InventoryIncomingReturnedInvoiceResource.post) | Post incoming returned invoice |
| `/api/inventory/v1/incoming_returned_invoice/unpost` | [`iiko.inventory.incoming_returned_invoice.unpost()`](inventory.md#iikocloudapi.resources.inventory.InventoryIncomingReturnedInvoiceResource.unpost) | Unpost incoming returned invoice |
| `/api/inventory/v1/incoming_returned_invoice/update` | [`iiko.inventory.incoming_returned_invoice.update()`](inventory.md#iikocloudapi.resources.inventory.InventoryIncomingReturnedInvoiceResource.update) | Edit incoming returned invoice |
| `/api/inventory/v1/sales_document/cancel` | [`iiko.inventory.sales_document.cancel()`](inventory.md#iikocloudapi.resources.inventory.InventorySalesDocumentResource.cancel) | Cancel sales document draft |
| `/api/inventory/v1/sales_document/create` | [`iiko.inventory.sales_document.create()`](inventory.md#iikocloudapi.resources.inventory.InventorySalesDocumentResource.create) | Create sales document |
| `/api/inventory/v1/sales_document/get` | [`iiko.inventory.sales_document.get()`](inventory.md#iikocloudapi.resources.inventory.InventorySalesDocumentResource.get) | Get sales document |
| `/api/inventory/v1/sales_document/list` | [`iiko.inventory.sales_document.list()`](inventory.md#iikocloudapi.resources.inventory.InventorySalesDocumentResource.list) | Export sales documents |
| `/api/inventory/v1/sales_document/post` | [`iiko.inventory.sales_document.post()`](inventory.md#iikocloudapi.resources.inventory.InventorySalesDocumentResource.post) | Post sales document |
| `/api/inventory/v1/sales_document/unpost` | [`iiko.inventory.sales_document.unpost()`](inventory.md#iikocloudapi.resources.inventory.InventorySalesDocumentResource.unpost) | Unpost sales document |
| `/api/inventory/v1/sales_document/update` | [`iiko.inventory.sales_document.update()`](inventory.md#iikocloudapi.resources.inventory.InventorySalesDocumentResource.update) | Edit sales document |
| `/api/inventory/v1/writeoff_document/cancel` | [`iiko.inventory.writeoff_document.cancel()`](inventory.md#iikocloudapi.resources.inventory.InventoryWriteoffDocumentResource.cancel) | Cancel write-off document draft |
| `/api/inventory/v1/writeoff_document/create` | [`iiko.inventory.writeoff_document.create()`](inventory.md#iikocloudapi.resources.inventory.InventoryWriteoffDocumentResource.create) | Create write-off document |
| `/api/inventory/v1/writeoff_document/get` | [`iiko.inventory.writeoff_document.get()`](inventory.md#iikocloudapi.resources.inventory.InventoryWriteoffDocumentResource.get) | Get write-off document by identifier |
| `/api/inventory/v1/writeoff_document/list` | [`iiko.inventory.writeoff_document.list()`](inventory.md#iikocloudapi.resources.inventory.InventoryWriteoffDocumentResource.list) | Export write-off documents |
| `/api/inventory/v1/writeoff_document/post` | [`iiko.inventory.writeoff_document.post()`](inventory.md#iikocloudapi.resources.inventory.InventoryWriteoffDocumentResource.post) | Post write-off document |
| `/api/inventory/v1/writeoff_document/unpost` | [`iiko.inventory.writeoff_document.unpost()`](inventory.md#iikocloudapi.resources.inventory.InventoryWriteoffDocumentResource.unpost) | Unpost write-off document |
| `/api/inventory/v1/writeoff_document/update` | [`iiko.inventory.writeoff_document.update()`](inventory.md#iikocloudapi.resources.inventory.InventoryWriteoffDocumentResource.update) | Edit write-off document |
| `/api/inventory/v1/internal_transfer/cancel` | [`iiko.inventory.internal_transfer.cancel()`](inventory.md#iikocloudapi.resources.inventory.InventoryInternalTransferResource.cancel) | Cancel internal transfer act draft |
| `/api/inventory/v1/internal_transfer/create` | [`iiko.inventory.internal_transfer.create()`](inventory.md#iikocloudapi.resources.inventory.InventoryInternalTransferResource.create) | Create internal transfer act |
| `/api/inventory/v1/internal_transfer/get` | [`iiko.inventory.internal_transfer.get()`](inventory.md#iikocloudapi.resources.inventory.InventoryInternalTransferResource.get) | Get internal transfer act by identifier |
| `/api/inventory/v1/internal_transfer/list` | [`iiko.inventory.internal_transfer.list()`](inventory.md#iikocloudapi.resources.inventory.InventoryInternalTransferResource.list) | Export internal transfer acts |
| `/api/inventory/v1/internal_transfer/post` | [`iiko.inventory.internal_transfer.post()`](inventory.md#iikocloudapi.resources.inventory.InventoryInternalTransferResource.post) | Post internal transfer act |
| `/api/inventory/v1/internal_transfer/unpost` | [`iiko.inventory.internal_transfer.unpost()`](inventory.md#iikocloudapi.resources.inventory.InventoryInternalTransferResource.unpost) | Unpost internal transfer act |
| `/api/inventory/v1/internal_transfer/update` | [`iiko.inventory.internal_transfer.update()`](inventory.md#iikocloudapi.resources.inventory.InventoryInternalTransferResource.update) | Edit internal transfer act |
| `/api/inventory/v1/production_document/cancel` | [`iiko.inventory.production_document.cancel()`](inventory.md#iikocloudapi.resources.inventory.InventoryProductionDocumentResource.cancel) | Cancel production document draft |
| `/api/inventory/v1/production_document/create` | [`iiko.inventory.production_document.create()`](inventory.md#iikocloudapi.resources.inventory.InventoryProductionDocumentResource.create) | Create production document |
| `/api/inventory/v1/production_document/get` | [`iiko.inventory.production_document.get()`](inventory.md#iikocloudapi.resources.inventory.InventoryProductionDocumentResource.get) | Get production document |
| `/api/inventory/v1/production_document/list` | [`iiko.inventory.production_document.list()`](inventory.md#iikocloudapi.resources.inventory.InventoryProductionDocumentResource.list) | Export production documents |
| `/api/inventory/v1/production_document/post` | [`iiko.inventory.production_document.post()`](inventory.md#iikocloudapi.resources.inventory.InventoryProductionDocumentResource.post) | Post production document |
| `/api/inventory/v1/production_document/unpost` | [`iiko.inventory.production_document.unpost()`](inventory.md#iikocloudapi.resources.inventory.InventoryProductionDocumentResource.unpost) | Unpost production document |
| `/api/inventory/v1/production_document/update` | [`iiko.inventory.production_document.update()`](inventory.md#iikocloudapi.resources.inventory.InventoryProductionDocumentResource.update) | Edit production document |
| `/api/inventory/v1/disassemble_document/cancel` | [`iiko.inventory.disassemble_document.cancel()`](inventory.md#iikocloudapi.resources.inventory.InventoryDisassembleDocumentResource.cancel) | Cancel disassemble document draft |
| `/api/inventory/v1/disassemble_document/create` | [`iiko.inventory.disassemble_document.create()`](inventory.md#iikocloudapi.resources.inventory.InventoryDisassembleDocumentResource.create) | Create disassemble document |
| `/api/inventory/v1/disassemble_document/get` | [`iiko.inventory.disassemble_document.get()`](inventory.md#iikocloudapi.resources.inventory.InventoryDisassembleDocumentResource.get) | Get disassemble document by identifier |
| `/api/inventory/v1/disassemble_document/list` | [`iiko.inventory.disassemble_document.list()`](inventory.md#iikocloudapi.resources.inventory.InventoryDisassembleDocumentResource.list) | Export disassemble documents |
| `/api/inventory/v1/disassemble_document/post` | [`iiko.inventory.disassemble_document.post()`](inventory.md#iikocloudapi.resources.inventory.InventoryDisassembleDocumentResource.post) | Post disassemble document |
| `/api/inventory/v1/disassemble_document/unpost` | [`iiko.inventory.disassemble_document.unpost()`](inventory.md#iikocloudapi.resources.inventory.InventoryDisassembleDocumentResource.unpost) | Unpost disassemble document |
| `/api/inventory/v1/disassemble_document/update` | [`iiko.inventory.disassemble_document.update()`](inventory.md#iikocloudapi.resources.inventory.InventoryDisassembleDocumentResource.update) | Edit disassemble document |
| `/api/inventory/v1/transformation_document/cancel` | [`iiko.inventory.transformation_document.cancel()`](inventory.md#iikocloudapi.resources.inventory.InventoryTransformationDocumentResource.cancel) | Cancel transformation document draft |
| `/api/inventory/v1/transformation_document/create` | [`iiko.inventory.transformation_document.create()`](inventory.md#iikocloudapi.resources.inventory.InventoryTransformationDocumentResource.create) | Create transformation document |
| `/api/inventory/v1/transformation_document/get` | [`iiko.inventory.transformation_document.get()`](inventory.md#iikocloudapi.resources.inventory.InventoryTransformationDocumentResource.get) | Get transformation document |
| `/api/inventory/v1/transformation_document/list` | [`iiko.inventory.transformation_document.list()`](inventory.md#iikocloudapi.resources.inventory.InventoryTransformationDocumentResource.list) | List transformation documents |
| `/api/inventory/v1/transformation_document/post` | [`iiko.inventory.transformation_document.post()`](inventory.md#iikocloudapi.resources.inventory.InventoryTransformationDocumentResource.post) | Post transformation document |
| `/api/inventory/v1/transformation_document/unpost` | [`iiko.inventory.transformation_document.unpost()`](inventory.md#iikocloudapi.resources.inventory.InventoryTransformationDocumentResource.unpost) | Unpost transformation document |
| `/api/inventory/v1/transformation_document/update` | [`iiko.inventory.transformation_document.update()`](inventory.md#iikocloudapi.resources.inventory.InventoryTransformationDocumentResource.update) | Edit transformation document |
| `/api/inventory/v1/incoming_inventory/cancel` | [`iiko.inventory.incoming_inventory.cancel()`](inventory.md#iikocloudapi.resources.inventory.InventoryIncomingInventoryResource.cancel) | Cancel inventory draft |
| `/api/inventory/v1/incoming_inventory/create` | [`iiko.inventory.incoming_inventory.create()`](inventory.md#iikocloudapi.resources.inventory.InventoryIncomingInventoryResource.create) | Create inventory |
| `/api/inventory/v1/incoming_inventory/get` | [`iiko.inventory.incoming_inventory.get()`](inventory.md#iikocloudapi.resources.inventory.InventoryIncomingInventoryResource.get) | Get inventory |
| `/api/inventory/v1/incoming_inventory/list` | [`iiko.inventory.incoming_inventory.list()`](inventory.md#iikocloudapi.resources.inventory.InventoryIncomingInventoryResource.list) | Export inventories |
| `/api/inventory/v1/incoming_inventory/post` | [`iiko.inventory.incoming_inventory.post()`](inventory.md#iikocloudapi.resources.inventory.InventoryIncomingInventoryResource.post) | Post inventory |
| `/api/inventory/v1/incoming_inventory/unpost` | [`iiko.inventory.incoming_inventory.unpost()`](inventory.md#iikocloudapi.resources.inventory.InventoryIncomingInventoryResource.unpost) | Unpost inventory |
| `/api/inventory/v1/incoming_inventory/update` | [`iiko.inventory.incoming_inventory.update()`](inventory.md#iikocloudapi.resources.inventory.InventoryIncomingInventoryResource.update) | Edit inventory |
| `/api/inventory/v1/counteragents/list` | [`iiko.inventory.counteragents.list()`](inventory.md#iikocloudapi.resources.inventory.InventoryCounteragentsResource.list) | Get counteragents list |
| `/api/inventory/v1/counteragents/pricelist/list` | [`iiko.inventory.counteragents.pricelist.list()`](inventory.md#iikocloudapi.resources.inventory.InventoryCounteragentsPricelistResource.list) | Get supplier price list |
| `/api/inventory/v1/organizations/settings/list` | [`iiko.inventory.organizations.settings.list()`](inventory.md#iikocloudapi.resources.inventory.InventoryOrganizationsSettingsResource.list) | Get corporation settings |
| `/api/inventory/v1/organizations/tree` | [`iiko.inventory.organizations.tree()`](inventory.md#iikocloudapi.resources.inventory.InventoryOrganizationsResource.tree) | Get terminal groups list |
| `/api/inventory/v1/stores/list` | [`iiko.inventory.stores.list()`](inventory.md#iikocloudapi.resources.inventory.InventoryStoresResource.list) | Get stores list |
| `/api/inventory/v1/accounting_categories/get` | [`iiko.inventory.accounting_categories.get()`](inventory.md#iikocloudapi.resources.inventory.InventoryAccountingCategoriesResource.get) | Get accounting category by ID |
| `/api/inventory/v1/accounting_categories/list` | [`iiko.inventory.accounting_categories.list()`](inventory.md#iikocloudapi.resources.inventory.InventoryAccountingCategoriesResource.list) | Get accounting categories list |
| `/api/inventory/v1/conceptions/get` | [`iiko.inventory.conceptions.get()`](inventory.md#iikocloudapi.resources.inventory.InventoryConceptionsResource.get) | Get conception by ID |
| `/api/inventory/v1/conceptions/list` | [`iiko.inventory.conceptions.list()`](inventory.md#iikocloudapi.resources.inventory.InventoryConceptionsResource.list) | Get conceptions list |
| `/api/inventory/v1/measure_units/get` | [`iiko.inventory.measure_units.get()`](inventory.md#iikocloudapi.resources.inventory.InventoryMeasureUnitsResource.get) | Get measure unit by ID |
| `/api/inventory/v1/measure_units/list` | [`iiko.inventory.measure_units.list()`](inventory.md#iikocloudapi.resources.inventory.InventoryMeasureUnitsResource.list) | Get measure units list |
| `/api/inventory/v1/payment_types/get` | [`iiko.inventory.payment_types.get()`](inventory.md#iikocloudapi.resources.inventory.InventoryPaymentTypesResource.get) | Get payment type by ID |
| `/api/inventory/v1/payment_types/list` | [`iiko.inventory.payment_types.list()`](inventory.md#iikocloudapi.resources.inventory.InventoryPaymentTypesResource.list) | Get payment types list |
| `/api/inventory/v1/stock_balance/list` | [`iiko.inventory.stock_balance.list()`](inventory.md#iikocloudapi.resources.inventory.InventoryStockBalanceResource.list) | Get stock balances by stores |

## [Finance](finance.md)

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/finance/v1/incoming_service/cancel` | [`iiko.finance.incoming_service.cancel()`](finance.md#iikocloudapi.resources.finance.FinanceIncomingServiceResource.cancel) | Cancel incoming service act draft |
| `/api/finance/v1/incoming_service/create` | [`iiko.finance.incoming_service.create()`](finance.md#iikocloudapi.resources.finance.FinanceIncomingServiceResource.create) | Create incoming service act |
| `/api/finance/v1/incoming_service/get` | [`iiko.finance.incoming_service.get()`](finance.md#iikocloudapi.resources.finance.FinanceIncomingServiceResource.get) | Get incoming service act |
| `/api/finance/v1/incoming_service/list` | [`iiko.finance.incoming_service.list()`](finance.md#iikocloudapi.resources.finance.FinanceIncomingServiceResource.list) | Export incoming service acts |
| `/api/finance/v1/incoming_service/post` | [`iiko.finance.incoming_service.post()`](finance.md#iikocloudapi.resources.finance.FinanceIncomingServiceResource.post) | Post incoming service act |
| `/api/finance/v1/incoming_service/unpost` | [`iiko.finance.incoming_service.unpost()`](finance.md#iikocloudapi.resources.finance.FinanceIncomingServiceResource.unpost) | Unpost incoming service act |
| `/api/finance/v1/incoming_service/update` | [`iiko.finance.incoming_service.update()`](finance.md#iikocloudapi.resources.finance.FinanceIncomingServiceResource.update) | Edit incoming service act |
| `/api/finance/v1/outgoing_service/cancel` | [`iiko.finance.outgoing_service.cancel()`](finance.md#iikocloudapi.resources.finance.FinanceOutgoingServiceResource.cancel) | Cancel outgoing service act draft |
| `/api/finance/v1/outgoing_service/create` | [`iiko.finance.outgoing_service.create()`](finance.md#iikocloudapi.resources.finance.FinanceOutgoingServiceResource.create) | Create outgoing service act |
| `/api/finance/v1/outgoing_service/get` | [`iiko.finance.outgoing_service.get()`](finance.md#iikocloudapi.resources.finance.FinanceOutgoingServiceResource.get) | Get outgoing service act |
| `/api/finance/v1/outgoing_service/list` | [`iiko.finance.outgoing_service.list()`](finance.md#iikocloudapi.resources.finance.FinanceOutgoingServiceResource.list) | Export outgoing service acts |
| `/api/finance/v1/outgoing_service/post` | [`iiko.finance.outgoing_service.post()`](finance.md#iikocloudapi.resources.finance.FinanceOutgoingServiceResource.post) | Post outgoing service act |
| `/api/finance/v1/outgoing_service/unpost` | [`iiko.finance.outgoing_service.unpost()`](finance.md#iikocloudapi.resources.finance.FinanceOutgoingServiceResource.unpost) | Unpost outgoing service act |
| `/api/finance/v1/outgoing_service/update` | [`iiko.finance.outgoing_service.update()`](finance.md#iikocloudapi.resources.finance.FinanceOutgoingServiceResource.update) | Edit outgoing service act |
| `/api/finance/v1/account_transactions/list` | [`iiko.finance.account_transactions.list()`](finance.md#iikocloudapi.resources.finance.FinanceAccountTransactionsResource.list) | Get account transactions |
| `/api/finance/v1/document_transactions/list` | [`iiko.finance.document_transactions.list()`](finance.md#iikocloudapi.resources.finance.FinanceDocumentTransactionsResource.list) | Get document transactions |
| `/api/finance/v1/account-type/list` | [`iiko.finance.account_type.list()`](finance.md#iikocloudapi.resources.finance.FinanceAccountTypeResource.list) | List of account types |
| `/api/finance/v1/cash-flow-category/create` | [`iiko.finance.cash_flow_category.create()`](finance.md#iikocloudapi.resources.finance.FinanceCashFlowCategoryResource.create) | Create cash flow category |
| `/api/finance/v1/cash-flow-category/delete` | [`iiko.finance.cash_flow_category.delete()`](finance.md#iikocloudapi.resources.finance.FinanceCashFlowCategoryResource.delete) | Delete cash flow category |
| `/api/finance/v1/cash-flow-category/get` | [`iiko.finance.cash_flow_category.get()`](finance.md#iikocloudapi.resources.finance.FinanceCashFlowCategoryResource.get) | Get cash flow category |
| `/api/finance/v1/cash-flow-category/list` | [`iiko.finance.cash_flow_category.list()`](finance.md#iikocloudapi.resources.finance.FinanceCashFlowCategoryResource.list) | List of cash flow categories |
| `/api/finance/v1/cash-flow-category/restore` | [`iiko.finance.cash_flow_category.restore()`](finance.md#iikocloudapi.resources.finance.FinanceCashFlowCategoryResource.restore) | Restore cash flow category |
| `/api/finance/v1/cash-flow-category/update` | [`iiko.finance.cash_flow_category.update()`](finance.md#iikocloudapi.resources.finance.FinanceCashFlowCategoryResource.update) | Update cash flow category |
| `/api/finance/v1/account/create` | [`iiko.finance.account.create()`](finance.md#iikocloudapi.resources.finance.FinanceAccountResource.create) | Create financial account |
| `/api/finance/v1/account/delete` | [`iiko.finance.account.delete()`](finance.md#iikocloudapi.resources.finance.FinanceAccountResource.delete) | Delete financial account |
| `/api/finance/v1/account/get` | [`iiko.finance.account.get()`](finance.md#iikocloudapi.resources.finance.FinanceAccountResource.get) | Get financial account |
| `/api/finance/v1/account/list` | [`iiko.finance.account.list()`](finance.md#iikocloudapi.resources.finance.FinanceAccountResource.list) | List of financial accounts |
| `/api/finance/v1/account/restore` | [`iiko.finance.account.restore()`](finance.md#iikocloudapi.resources.finance.FinanceAccountResource.restore) | Restore financial account |
| `/api/finance/v1/account/update` | [`iiko.finance.account.update()`](finance.md#iikocloudapi.resources.finance.FinanceAccountResource.update) | Update financial account |
| `/api/finance/v1/item-category/list` | [`iiko.finance.item_category.list()`](finance.md#iikocloudapi.resources.finance.FinanceItemCategoryResource.list) | Get a list of fiscal categories |
| `/api/finance/v1/tax-category/list` | [`iiko.finance.tax_category.list()`](finance.md#iikocloudapi.resources.finance.FinanceTaxCategoryResource.list) | Get a list of tax categories |
| `/api/finance/v1/account-posting/list` | [`iiko.finance.account_posting.list()`](finance.md#iikocloudapi.resources.finance.FinanceAccountPostingResource.list) | Account postings |
| `/api/finance/v1/balance-sheet/list` | [`iiko.finance.balance_sheet.list()`](finance.md#iikocloudapi.resources.finance.FinanceBalanceSheetResource.list) | Balance sheet |
| `/api/finance/v1/chart-of-accounts/list` | [`iiko.finance.chart_of_accounts.list()`](finance.md#iikocloudapi.resources.finance.FinanceChartOfAccountsResource.list) | Chart of accounts |

## [Nomenclature](nomenclature.md)

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/nomenclature/v2/group/create` | [`iiko.nomenclature.group.create()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureGroupResource.create) | Create a nomenclature group (v2) |
| `/api/nomenclature/v2/group/delete` | [`iiko.nomenclature.group.delete()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureGroupResource.delete) | Delete nomenclature groups (v2) |
| `/api/nomenclature/v2/group/list` | [`iiko.nomenclature.group.list()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureGroupResource.list) | Get a list of nomenclature groups (v2) |
| `/api/nomenclature/v2/group/restore` | [`iiko.nomenclature.group.restore()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureGroupResource.restore) | Restore nomenclature groups (v2) |
| `/api/nomenclature/v2/group/update` | [`iiko.nomenclature.group.update()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureGroupResource.update) | Update a nomenclature group (v2) |
| `/api/nomenclature/v2/product/create` | [`iiko.nomenclature.product.create()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureProductResource.create) | Create a product (v2) |
| `/api/nomenclature/v2/product/delete` | [`iiko.nomenclature.product.delete()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureProductResource.delete) | Delete products (v2) |
| `/api/nomenclature/v2/product/list` | [`iiko.nomenclature.product.list()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureProductResource.list) | Get a list of products (v2) |
| `/api/nomenclature/v2/product/restore` | [`iiko.nomenclature.product.restore()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureProductResource.restore) | Restore products (v2) |
| `/api/nomenclature/v2/product/update` | [`iiko.nomenclature.product.update()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureProductResource.update) | Update a product (v2) |
| `/api/nomenclature/v2/product/update_barcodes` | [`iiko.nomenclature.product.update_barcodes()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureProductResource.update_barcodes) | Update product barcodes (v2) |
| `/api/nomenclature/v2/assembly-chart/assembled` | [`iiko.nomenclature.assembly_chart.assembled()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureAssemblyChartResource.assembled) | Get an assembled chart |
| `/api/nomenclature/v2/assembly-chart/create` | [`iiko.nomenclature.assembly_chart.create()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureAssemblyChartResource.create) | Create an assembly chart (v2) |
| `/api/nomenclature/v2/assembly-chart/delete` | [`iiko.nomenclature.assembly_chart.delete()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureAssemblyChartResource.delete) | Delete an assembly chart (v2) |
| `/api/nomenclature/v2/assembly-chart/get` | [`iiko.nomenclature.assembly_chart.get()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureAssemblyChartResource.get) | Get an assembly chart by ID (v2) |
| `/api/nomenclature/v2/assembly-chart/list` | [`iiko.nomenclature.assembly_chart.list()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureAssemblyChartResource.list) | Get a list of assembly charts by product (v2) |
| `/api/nomenclature/v2/assembly-chart/prepared` | [`iiko.nomenclature.assembly_chart.prepared()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureAssemblyChartResource.prepared) | Get a prepared chart (breakdown to store items) |
| `/api/nomenclature/v2/assembly-chart/tree` | [`iiko.nomenclature.assembly_chart.tree()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureAssemblyChartResource.tree) | Get an assembly chart tree |
| `/api/nomenclature/v2/assembly-chart/update` | [`iiko.nomenclature.assembly_chart.update()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureAssemblyChartResource.update) | Update an assembly chart (v2) |
| `/api/nomenclature/v1/product-scale/create` | [`iiko.nomenclature.product_scale.create()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureProductScaleResource.create) | Create a product size scale |
| `/api/nomenclature/v1/product-scale/delete` | [`iiko.nomenclature.product_scale.delete()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureProductScaleResource.delete) | Delete a product size scale |
| `/api/nomenclature/v1/product-scale/get` | [`iiko.nomenclature.product_scale.get()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureProductScaleResource.get) | Get a product size scale by ID |
| `/api/nomenclature/v1/product-scale/list` | [`iiko.nomenclature.product_scale.list()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureProductScaleResource.list) | Get a list of product size scales |
| `/api/nomenclature/v1/product-scale/update` | [`iiko.nomenclature.product_scale.update()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureProductScaleResource.update) | Update a product size scale |
| `/api/nomenclature/v1/nomenclature/category/create` | [`iiko.nomenclature.nomenclature.category.create()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureNomenclatureCategoryResource.create) | Create a product category |
| `/api/nomenclature/v1/nomenclature/category/delete` | [`iiko.nomenclature.nomenclature.category.delete()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureNomenclatureCategoryResource.delete) | Delete a product category |
| `/api/nomenclature/v1/nomenclature/category/list` | [`iiko.nomenclature.nomenclature.category.list()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureNomenclatureCategoryResource.list) | Get a list of product categories |
| `/api/nomenclature/v1/nomenclature/category/restore` | [`iiko.nomenclature.nomenclature.category.restore()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureNomenclatureCategoryResource.restore) | Restore a product category |
| `/api/nomenclature/v1/nomenclature/category/update` | [`iiko.nomenclature.nomenclature.category.update()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureNomenclatureCategoryResource.update) | Update a product category |
| `/api/nomenclature/v1/allergen-group/list` | [`iiko.nomenclature.allergen_group.list()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureAllergenGroupResource.list) | Get a list of allergen groups |
| `/api/nomenclature/v1/amount-unit/list` | [`iiko.nomenclature.amount_unit.list()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureAmountUnitResource.list) | Get a list of amount units |
| `/api/nomenclature/v1/container/list` | [`iiko.nomenclature.container.list()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureContainerResource.list) | Get a list of containers |
| `/api/nomenclature/v1/custom-category/list` | [`iiko.nomenclature.custom_category.list()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureCustomCategoryResource.list) | Get a list of custom categories |
| `/api/nomenclature/v1/menu/list` | [`iiko.nomenclature.menu.list()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureMenuResource.list) | Get a list of menu sections |
| `/api/nomenclature/v1/modifier-schema/list` | [`iiko.nomenclature.modifier_schema.list()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureModifierSchemaResource.list) | Get a list of modifier schemas |
| `/api/nomenclature/v1/outer_economic_activity_nomenclature_codes/get` | [`iiko.nomenclature.outer_economic_activity_nomenclature_codes.get()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureOuterEconomicActivityNomenclatureCodesResource.get) | Get a foreign economic activity commodity code by ID |
| `/api/nomenclature/v1/outer_economic_activity_nomenclature_codes/list` | [`iiko.nomenclature.outer_economic_activity_nomenclature_codes.list()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureOuterEconomicActivityNomenclatureCodesResource.list) | Get the foreign economic activity commodity code directory |
| `/api/nomenclature/v1/place-type/list` | [`iiko.nomenclature.place_type.list()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclaturePlaceTypeResource.list) | Get a list of preparation place types |
| `/api/nomenclature/v1/producer/list` | [`iiko.nomenclature.producer.list()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureProducerResource.list) | Get a list of producers |
| `/api/nomenclature/v1/product-size/list` | [`iiko.nomenclature.product_size.list()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureProductSizeResource.list) | Get a list of product sizes |
| `/api/nomenclature/v1/product-tag/list` | [`iiko.nomenclature.product_tag.list()`](nomenclature.md#iikocloudapi.resources.nomenclature.NomenclatureProductTagResource.list) | Get a list of product tags |

## [Employees](employees.md)

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/employees/v1/employee/create` | [`iiko.employees.employee.create()`](employees.md#iikocloudapi.resources.employees.EmployeesEmployeeResource.create) | Create employee |
| `/api/employees/v1/employee/fire` | [`iiko.employees.employee.fire()`](employees.md#iikocloudapi.resources.employees.EmployeesEmployeeResource.fire) | Fire employees |
| `/api/employees/v1/employee/get` | [`iiko.employees.employee.get()`](employees.md#iikocloudapi.resources.employees.EmployeesEmployeeResource.get) | Get employee |
| `/api/employees/v1/employee/list` | [`iiko.employees.employee.list()`](employees.md#iikocloudapi.resources.employees.EmployeesEmployeeResource.list) | List of employees |
| `/api/employees/v1/employee/restore` | [`iiko.employees.employee.restore()`](employees.md#iikocloudapi.resources.employees.EmployeesEmployeeResource.restore) | Restore employee |
| `/api/employees/v1/employee/update` | [`iiko.employees.employee.update()`](employees.md#iikocloudapi.resources.employees.EmployeesEmployeeResource.update) | Update employee |
| `/api/employees/v1/positions/get` | [`iiko.employees.positions.get()`](employees.md#iikocloudapi.resources.employees.EmployeesPositionsResource.get) | Get employee position by identifier |
| `/api/employees/v1/positions/list` | [`iiko.employees.positions.list()`](employees.md#iikocloudapi.resources.employees.EmployeesPositionsResource.list) | List employee positions |
| `/api/employees/v1/attendance/create` | [`iiko.employees.attendance.create()`](employees.md#iikocloudapi.resources.employees.EmployeesAttendanceResource.create) | Create employee attendance |
| `/api/employees/v1/attendance/delete` | [`iiko.employees.attendance.delete()`](employees.md#iikocloudapi.resources.employees.EmployeesAttendanceResource.delete) | Delete employee attendance |
| `/api/employees/v1/attendance/list` | [`iiko.employees.attendance.list()`](employees.md#iikocloudapi.resources.employees.EmployeesAttendanceResource.list) | List employee attendances |
| `/api/employees/v1/attendance/update` | [`iiko.employees.attendance.update()`](employees.md#iikocloudapi.resources.employees.EmployeesAttendanceResource.update) | Update employee attendance |
| `/api/employees/v1/attendance-type/list` | [`iiko.employees.attendance_type.list()`](employees.md#iikocloudapi.resources.employees.EmployeesAttendanceTypeResource.list) | List attendance types |

## [Reports](reports.md)

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/reporting/v1/olap/columns/get` | [`iiko.reporting.olap.columns.get()`](reports.md#iikocloudapi.resources.reporting.ReportingOlapColumnsResource.get) | Get OLAP report columns |
| `/api/reporting/v1/olap/get` | [`iiko.reporting.olap.get()`](reports.md#iikocloudapi.resources.reporting.ReportingOlapResource.get) | Run OLAP report |
| `/api/reporting/v1/olap/presets/get` | [`iiko.reporting.olap.presets.get()`](reports.md#iikocloudapi.resources.reporting.ReportingOlapPresetsResource.get) | Get saved OLAP preset data |
| `/api/reporting/v1/olap/presets/list` | [`iiko.reporting.olap.presets.list()`](reports.md#iikocloudapi.resources.reporting.ReportingOlapPresetsResource.list) | Get saved OLAP presets |
| `/api/reporting/v1/income-plan/list` | [`iiko.reporting.income_plan.list()`](reports.md#iikocloudapi.resources.reporting.ReportingIncomePlanResource.list) | Get income plan |

## [Terminals](terminals.md)

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/terminals/v1/terminals/list` | [`iiko.terminals.terminals.list()`](terminals.md#iikocloudapi.resources.terminals.TerminalsTerminalsResource.list) | List of terminals |
| `/api/terminals/v1/cash-registers/list` | [`iiko.terminals.cash_registers.list()`](terminals.md#iikocloudapi.resources.terminals.TerminalsCashRegistersResource.list) | List of cash registers |

## [Platform](platform.md)

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/platform/v1/events/list` | [`iiko.platform.events.list()`](platform.md#iikocloudapi.resources.platform.PlatformEventsResource.list) | List of events |
| `/api/platform/v1/events/metadata/list` | [`iiko.platform.events.metadata.list()`](platform.md#iikocloudapi.resources.platform.PlatformEventsMetadataResource.list) | Event groups and types |
