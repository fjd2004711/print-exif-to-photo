def reorder_address(address):
    address_parts = [part.strip() for part in address.split(',')]

    autonomous_region = ''
    province_or_city = ''
    city = ''
    county = ''
    district = ''
    street = ''
    specific = ''

    for part in address_parts:
        if '自治区' in part and not autonomous_region:
            autonomous_region = part
        elif '省' in part and not province_or_city:
            province_or_city = part
        elif '市' in part:
            if part.endswith('市') and not city:
                city = part
        elif '县' in part and not county:
            county = part
        elif '区' in part and not district:
            district = part
        elif any(sub in part for sub in ['街道', '乡', '镇']) and not street:
            street = part
        elif any(sub in part for sub in ['路', '街', '巷']):
            specific = specific + ', ' + part if specific else part
        else:
            specific = specific + ', ' + part if specific else part

    # 过滤空值并拼接地址
    reordered_parts = filter(None, [autonomous_region, province_or_city, city, county, district, street, specific])
    sorted_address = ', '.join(reordered_parts)
    return sorted_address
