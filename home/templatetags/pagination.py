from django import template

register=template.Library()

@register.filter
def get_display_range(page_obj,num):
    num=int(num)
    current_page_index=page_obj.number
    first_page_index=1
    last_page_index=page_obj.paginator.num_pages

    if last_page_index<=num*2+1:
        # 总页数长度小于等于需求页数时，直接以总页数为长度
        return range(first_page_index, last_page_index + 1)
    else:
        # 总页数大于需求页数时，判断左右哪边超出长度（总页数大时，最多只会有一边超出）
        # 然后根据需求页数直接算出剩余页数
        if current_page_index-num<first_page_index:
            start_index = first_page_index
            end_index=first_page_index+num*2
        elif current_page_index+num>last_page_index:
            start_index = last_page_index-num*2
            end_index=last_page_index
        else:
            start_index = current_page_index - num
            end_index = current_page_index + num
        return range(start_index,end_index+1)