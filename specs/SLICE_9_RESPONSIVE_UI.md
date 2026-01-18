# Slice 9: Responsive UI for Web & Mobile

**STATUS: PLANNING**

## Overview

**Objective:** Make the entire UI fully responsive for desktop, tablet, and mobile devices.

**Success Criteria:**

- [ ] All pages usable on mobile (320px - 480px)
- [ ] All pages usable on tablet (768px - 1024px)
- [ ] All pages usable on desktop (1024px+)
- [ ] Tables scroll horizontally on small screens
- [ ] Forms stack vertically on mobile
- [ ] Touch targets minimum 44px for mobile
- [ ] Navigation works on all screen sizes
- [ ] Modals fit screen on mobile
- [ ] All tests pass

---

## Current State Analysis

### Templates with Good Responsive Design
- `base.html` - Has viewport meta, responsive nav
- `dashboard.html` - Uses responsive grids (`md:grid-cols-3`, `lg:grid-cols-2`)
- `logs.html` - Has `overflow-x-auto` for tables
- Filter partials - Use responsive grids

### Templates Needing Work
| Template | Issues |
|----------|--------|
| `products.html` | No responsive table, fixed modal, no mobile breakpoints |
| `stores.html` | No responsive table, fixed modal, no mobile breakpoints |
| `tracked-items.html` | Non-responsive form grids (`grid-cols-2`, `grid-cols-3`) |
| `dashboard.html` | Table columns overflow, small touch targets |

---

## Responsive Breakpoints

Using Tailwind CSS default breakpoints:

| Prefix | Min Width | Devices |
|--------|-----------|---------|
| (none) | 0px | Mobile first (default) |
| `sm:` | 640px | Large phones, small tablets |
| `md:` | 768px | Tablets |
| `lg:` | 1024px | Laptops, desktops |
| `xl:` | 1280px | Large desktops |

**Strategy:** Mobile-first approach. Base styles for mobile, then add complexity for larger screens.

---

## Implementation Plan

### Phase 1: Navigation & Base Layout

**File:** `base.html`

Current nav is horizontal. Add hamburger menu for mobile:

```html
<!-- Mobile menu button (hidden on md+) -->
<button @click="mobileMenuOpen = !mobileMenuOpen" class="md:hidden p-2">
    <svg class="w-6 h-6"><!-- hamburger icon --></svg>
</button>

<!-- Desktop nav (hidden on mobile) -->
<nav class="hidden md:flex space-x-4">
    <!-- existing nav links -->
</nav>

<!-- Mobile nav (shown when open) -->
<nav x-show="mobileMenuOpen" class="md:hidden flex flex-col space-y-2 p-4">
    <!-- nav links stacked vertically -->
</nav>
```

---

### Phase 2: Dashboard Improvements

**File:** `dashboard.html`

1. **Table responsiveness** - Add horizontal scroll wrapper:
```html
<div class="overflow-x-auto -mx-4 sm:mx-0">
    <table class="min-w-full">
```

2. **Hide less important columns on mobile:**
```html
<th class="hidden sm:table-cell">Unit Price</th>
<th class="hidden md:table-cell">Last Checked</th>
```

3. **Stack info on mobile:**
```html
<!-- On mobile: stack product name and store -->
<td>
    <div class="font-medium">{product_name}</div>
    <div class="text-sm text-gray-500 sm:hidden">{store_name}</div>
</td>
<td class="hidden sm:table-cell">{store_name}</td>
```

4. **Improve deal alert for mobile:**
```html
<div class="flex flex-col sm:flex-row sm:items-center gap-2">
```

5. **Scheduler panel - stack on mobile:**
```html
<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
```

---

### Phase 3: Products Page

**File:** `products.html`

1. **Add table scroll wrapper:**
```html
<div class="overflow-x-auto">
    <table class="min-w-full divide-y divide-gray-200">
```

2. **Responsive action buttons:**
```html
<!-- Stack buttons on mobile, inline on larger -->
<div class="flex flex-col sm:flex-row gap-2">
    <button>Edit</button>
    <button>Delete</button>
</div>
```

3. **Card layout option for mobile:**
```html
<!-- Table for desktop -->
<div class="hidden sm:block">
    <table>...</table>
</div>

<!-- Card layout for mobile -->
<div class="sm:hidden space-y-4">
    {% for product in products %}
    <div class="bg-white rounded-lg shadow p-4">
        <div class="font-semibold">{{ product.name }}</div>
        <div class="text-sm text-gray-500">{{ product.category }}</div>
        <div class="text-lg font-bold text-green-600">Target: €{{ product.target_price }}</div>
        <div class="flex gap-2 mt-2">
            <button>Edit</button>
            <button>Delete</button>
        </div>
    </div>
    {% endfor %}
</div>
```

4. **Modal improvements:**
```html
<!-- Full screen on mobile, centered modal on desktop -->
<div class="fixed inset-0 sm:inset-auto sm:top-1/2 sm:left-1/2 sm:-translate-x-1/2 sm:-translate-y-1/2
            w-full h-full sm:w-full sm:max-w-md sm:h-auto
            bg-white sm:rounded-lg overflow-y-auto">
```

---

### Phase 4: Stores Page

**File:** `stores.html`

Same patterns as products.html:
1. Table scroll wrapper
2. Responsive action buttons
3. Card layout for mobile
4. Full-screen modal on mobile

---

### Phase 5: Tracked Items Page

**File:** `tracked-items.html`

1. **Fix form grids:**
```html
<!-- Before -->
<div class="grid grid-cols-2 gap-4">

<!-- After -->
<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
```

```html
<!-- Before -->
<div class="grid grid-cols-3 gap-4">

<!-- After -->
<div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
```

2. **Table responsiveness:**
- Hide URL column on mobile (show truncated in product name cell)
- Hide "Items/Lot" on mobile
- Stack product/store info on mobile

3. **Improve touch targets:**
```html
<!-- Larger buttons on mobile -->
<button class="p-2 sm:p-1 min-h-[44px] sm:min-h-0">
```

---

### Phase 6: Logs Page

**File:** `logs.html`

1. **Filter panel - stack on mobile:**
```html
<!-- Already has grid-cols-1 md:grid-cols-5, verify it works -->
```

2. **Table improvements:**
- Already has `overflow-x-auto`
- Hide less important columns on mobile
- Consider card layout for error logs

3. **Tab navigation - scrollable on mobile:**
```html
<div class="flex overflow-x-auto border-b">
    <button class="whitespace-nowrap px-4 py-2">Extraction Logs</button>
    <button class="whitespace-nowrap px-4 py-2">Error Logs</button>
</div>
```

---

## Mobile-Specific Patterns

### 1. Horizontal Scroll Tables
```html
<div class="overflow-x-auto -mx-4 px-4 sm:mx-0 sm:px-0">
    <table class="min-w-full">
        <!-- table content -->
    </table>
</div>
```

### 2. Responsive Hide/Show
```html
<!-- Hide on mobile -->
<td class="hidden sm:table-cell">...</td>

<!-- Show only on mobile -->
<span class="sm:hidden">...</span>
```

### 3. Touch-Friendly Buttons
```html
<button class="px-4 py-3 sm:px-3 sm:py-2 text-base sm:text-sm min-h-[44px] sm:min-h-0">
    Action
</button>
```

### 4. Full-Screen Modals on Mobile
```html
<div x-show="modalOpen"
     class="fixed inset-0 z-50
            flex items-end sm:items-center justify-center">
    <div class="w-full h-[90vh] sm:h-auto sm:max-h-[90vh]
                sm:max-w-lg sm:mx-4
                bg-white rounded-t-xl sm:rounded-lg
                overflow-y-auto">
        <!-- Modal content -->
    </div>
</div>
```

### 5. Card Layout for Mobile Lists
```html
<!-- Desktop: Table -->
<div class="hidden sm:block">
    <table>...</table>
</div>

<!-- Mobile: Cards -->
<div class="sm:hidden space-y-3">
    <div class="bg-white rounded-lg shadow p-4">
        <!-- Card content -->
    </div>
</div>
```

---

## Testing Checklist

### Mobile (320px - 480px)
- [ ] Navigation menu works
- [ ] Dashboard readable, no horizontal overflow
- [ ] Can create/edit products
- [ ] Can create/edit stores
- [ ] Can create/edit tracked items
- [ ] Can view logs
- [ ] Modals fit screen
- [ ] Buttons are tappable (44px min)

### Tablet (768px - 1024px)
- [ ] Two-column layouts work
- [ ] Tables readable
- [ ] Forms have good layout
- [ ] Modals centered properly

### Desktop (1024px+)
- [ ] Full layouts display
- [ ] No regressions from current design
- [ ] All columns visible

---

## Implementation Order

### Phase 1: Base & Navigation
1. [ ] Add mobile menu to base.html
2. [ ] Test navigation on all screen sizes
3. [ ] Write tests for mobile nav

### Phase 2: Dashboard
1. [ ] Add table scroll wrapper
2. [ ] Implement responsive column hiding
3. [ ] Stack scheduler panel on mobile
4. [ ] Test deal alerts on mobile

### Phase 3: Products Page
1. [ ] Add table scroll wrapper
2. [ ] Create mobile card layout
3. [ ] Fix modal for mobile
4. [ ] Improve touch targets

### Phase 4: Stores Page
1. [ ] Same improvements as products
2. [ ] Test CRUD on mobile

### Phase 5: Tracked Items
1. [ ] Fix form grid breakpoints
2. [ ] Add table responsiveness
3. [ ] Fix modal layout
4. [ ] Test full workflow on mobile

### Phase 6: Logs Page
1. [ ] Verify filter responsiveness
2. [ ] Improve table columns for mobile
3. [ ] Test tab navigation

---

## Files to Modify

| File | Changes |
|------|---------|
| `app/templates/base.html` | Add mobile hamburger menu |
| `app/templates/dashboard.html` | Table scroll, column hiding, stack panels |
| `app/templates/products.html` | Table scroll, card layout, modal fix |
| `app/templates/stores.html` | Table scroll, card layout, modal fix |
| `app/templates/tracked-items.html` | Fix form grids, table scroll, modal fix |
| `app/templates/logs.html` | Verify/improve table responsiveness |

---

## Definition of Done

Slice 9 is complete when:

- [ ] Mobile hamburger menu works
- [ ] All tables scroll horizontally on small screens
- [ ] All forms stack properly on mobile
- [ ] All modals fit mobile screens
- [ ] Touch targets are 44px minimum
- [ ] No horizontal page overflow on any page
- [ ] Card layouts work on mobile for list pages
- [ ] All existing tests pass
- [ ] Manual testing on mobile device/emulator complete
- [ ] Documentation updated

---

## Browser/Device Testing

Test on:
- [ ] Chrome DevTools mobile emulation (iPhone SE, iPhone 12, Pixel 5)
- [ ] Firefox responsive mode
- [ ] Real mobile device (if available)
- [ ] Tablet emulation (iPad)

---

**Status: PLANNING** (January 2026)
