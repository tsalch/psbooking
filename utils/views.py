from hotels.models import Hotel
from django.db.models import Avg, Min, Count, OuterRef


def hotel_query(obj):
    hotel_list = obj.annotate(count_rev=Count('reviews', distinct=True), avg_rate=Avg('reviews__rate'))
    hotel_list = hotel_list.prefetch_related('rooms').annotate(min_price=Min('rooms__price')).all()
    hotel_list = hotel_list.select_related('country', 'town')
    return hotel_list


def book_rev(queryset, subquery, user):
    if user.profile.role == 'u':
        queryset = queryset.filter(user=user)
    subquery = subquery.objects.filter(user=OuterRef('user_id'), hotel=OuterRef('hotel_id'))
    queryset = queryset.select_related('hotel__country', 'hotel__town')
    return (queryset, subquery,)
