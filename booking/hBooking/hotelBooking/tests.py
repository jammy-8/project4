from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import booking, hotelTypes
from datetime import date, timedelta
from django.utils import timezone


class IndexViewTest(TestCase):
    """Test cases for the index view."""

    def setUp(self):
        self.client = Client()
        self.hotel1 = hotelTypes.objects.create(hotel_type='Deluxe Room', hotel_img='path/to/img1.jpg')
        self.hotel2 = hotelTypes.objects.create(hotel_type='Suite Room', hotel_img='path/to/img2.jpg')

    def test_index_view_accessible(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_index_template_used(self):
        response = self.client.get(reverse('index'))
        self.assertTemplateUsed(response, 'hBooking/index.html')

    def test_index_contains_hotel_types(self):
        response = self.client.get(reverse('index'))
        self.assertIn('hotelTypesList', response.context)
        hotel_list = response.context['hotelTypesList']
        self.assertEqual(len(hotel_list), 2)
        self.assertEqual(hotel_list[0]['hotel_type'], 'Deluxe Room')


class LoginViewTest(TestCase):
    """Test cases for the login view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hBooking/login.html')

    def test_authenticated_user_redirected_to_index(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, reverse('index'))

    def test_valid_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertRedirects(response, reverse('index'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_invalid_login_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hBooking/login.html')

    def test_login_with_next_parameter(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'password123',
            'next': reverse('booking')
        }, follow=False)
        self.assertEqual(response.status_code, 302)


class SignupViewTest(TestCase):
    """Test cases for the signup view."""

    def setUp(self):
        self.client = Client()

    def test_signup_page_loads(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hBooking/signup.html')

    def test_authenticated_user_redirected_from_signup(self):
        user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('signup'))
        self.assertRedirects(response, reverse('index'))

    def test_valid_signup(self):
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_signup_password_mismatch(self):
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password1': 'StrongPass123!',
            'password2': 'DifferentPass123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_signup_duplicate_username(self):
        User.objects.create_user(username='testuser', password='password123')
        response = self.client.post(reverse('signup'), {
            'username': 'testuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        })
        self.assertEqual(response.status_code, 200)


class LogoutViewTest(TestCase):
    """Test cases for the logout view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')

    def test_logout_redirects_to_index(self):
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('index'))

    def test_user_logged_out_after_logout(self):
        self.client.get(reverse('logout'))
        response = self.client.get(reverse('index'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class BookingViewTest(TestCase):
    """Test cases for the booking view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='12345')
        self.hotel = hotelTypes.objects.create(hotel_type='Deluxe Room', hotel_img='path/to/img.jpg')
        self.tomorrow = timezone.now().date() + timedelta(days=1)
        self.day_after_tomorrow = timezone.now().date() + timedelta(days=2)

    def test_booking_page_requires_login(self):
        response = self.client.get(reverse('booking'))
        self.assertNotEqual(response.status_code, 200)

    def test_logged_in_user_can_access(self):
        self.client.login(username='test', password='12345')
        response = self.client.get(reverse('booking'))
        self.assertEqual(response.status_code, 200)

    def test_booking_page_displays_hotel_types(self):
        self.client.login(username='test', password='12345')
        response = self.client.get(reverse('booking'))
        self.assertIn('hotel_types', response.context)

    def test_create_booking_valid(self):
        self.client.login(username='test', password='12345')
        response = self.client.post(reverse('booking'), {
            'check-in': self.tomorrow.strftime('%Y-%m-%d'),
            'check-out': self.day_after_tomorrow.strftime('%Y-%m-%d'),
            'room': self.hotel.hotel_id
        })
        self.assertRedirects(response, reverse('booking_success'))
        self.assertTrue(booking.objects.filter(user=self.user).exists())

    def test_create_booking_increments_count(self):
        self.client.login(username='test', password='12345')
        self.assertEqual(booking.objects.filter(user=self.user).count(), 0)
        
        self.client.post(reverse('booking'), {
            'check-in': self.tomorrow.strftime('%Y-%m-%d'),
            'check-out': self.day_after_tomorrow.strftime('%Y-%m-%d'),
            'room': self.hotel.hotel_id
        })
        self.assertEqual(booking.objects.filter(user=self.user).count(), 1)

    def test_booking_creation_requires_authentication(self):
        response = self.client.post(reverse('booking'), {
            'check-in': self.tomorrow.strftime('%Y-%m-%d'),
            'check-out': self.day_after_tomorrow.strftime('%Y-%m-%d'),
            'room': self.hotel.hotel_id
        })
        self.assertNotEqual(response.status_code, 200)


class BookingSuccessViewTest(TestCase):
    """Test cases for the booking success view."""

    def setUp(self):
        self.client = Client()

    def test_booking_success_page_loads(self):
        response = self.client.get(reverse('booking_success'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hBooking/booking_success.html')


class MyBookingsViewTest(TestCase):
    """Test cases for the my_bookings view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='12345')
        self.hotel = hotelTypes.objects.create(hotel_type='Deluxe Room', hotel_img='path/to/img.jpg')
        self.tomorrow = timezone.now().date() + timedelta(days=1)
        self.day_after_tomorrow = timezone.now().date() + timedelta(days=2)

    def test_my_bookings_shows_user_bookings(self):
        booking.objects.create(
            user=self.user,
            check_in_date=self.tomorrow,
            check_out_date=self.day_after_tomorrow,
            hotel_type=self.hotel
        )
        self.client.login(username='test', password='12345')
        response = self.client.get(reverse('my_bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('bookings', response.context)
        self.assertEqual(response.context['bookings'].count(), 1)

    def test_my_bookings_only_shows_user_bookings(self):
        other_user = User.objects.create_user(username='other', password='12345')
        booking.objects.create(
            user=self.user,
            check_in_date=self.tomorrow,
            check_out_date=self.day_after_tomorrow,
            hotel_type=self.hotel
        )
        booking.objects.create(
            user=other_user,
            check_in_date=self.tomorrow,
            check_out_date=self.day_after_tomorrow,
            hotel_type=self.hotel
        )
        self.client.login(username='test', password='12345')
        response = self.client.get(reverse('my_bookings'))
        self.assertEqual(response.context['bookings'].count(), 1)

    def test_my_bookings_template_used(self):
        self.client.login(username='test', password='12345')
        response = self.client.get(reverse('my_bookings'))
        self.assertTemplateUsed(response, 'hBooking/my_bookings.html')

#
class UpdateBookingViewTest(TestCase):
    """Test cases for the update booking view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='12345')
        self.other_user = User.objects.create_user(username='other', password='12345')
        self.hotel = hotelTypes.objects.create(hotel_type='Deluxe Room', hotel_img='path/to/img.jpg')
        self.tomorrow = timezone.now().date() + timedelta(days=1)
        self.day_after_tomorrow = timezone.now().date() + timedelta(days=2)
        self.three_days = timezone.now().date() + timedelta(days=3)
        self.booking = booking.objects.create(
            user=self.user,
            check_in_date=self.tomorrow,
            check_out_date=self.day_after_tomorrow,
            hotel_type=self.hotel
        )

    print()

    def test_update_booking_valid(self):
        self.client.login(username='test', password='12345')
        response = self.client.post(
            reverse('update_bookings', args=[self.booking.booking_id]),
            {
                'check-in': self.day_after_tomorrow.strftime('%Y-%m-%d'),
                'check-out': self.three_days.strftime('%Y-%m-%d'),
                'room': self.hotel.hotel_id
            }
        )
        self.assertRedirects(response, reverse('my_bookings'))
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.check_in_date, self.day_after_tomorrow)

    def test_update_booking_with_past_date(self):
        self.client.login(username='test', password='12345')
        past_date = timezone.now().date() - timedelta(days=1)
        response = self.client.post(
            reverse('update_bookings', args=[self.booking.booking_id]),
            {
                'check-in': past_date.strftime('%Y-%m-%d'),
                'check-out': self.tomorrow.strftime('%Y-%m-%d'),
                'room': self.hotel.hotel_id
            }
        )
        self.assertEqual(response.status_code, 200)


class DeleteBookingViewTest(TestCase):
    """Test cases for the delete booking view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='12345')
        self.other_user = User.objects.create_user(username='other', password='12345')
        self.hotel = hotelTypes.objects.create(hotel_type='Deluxe Room', hotel_img='path/to/img.jpg')
        self.tomorrow = timezone.now().date() + timedelta(days=1)
        self.day_after_tomorrow = timezone.now().date() + timedelta(days=2)
        self.booking = booking.objects.create(
            user=self.user,
            check_in_date=self.tomorrow,
            check_out_date=self.day_after_tomorrow,
            hotel_type=self.hotel
        )

    def test_delete_booking_valid(self):
        self.client.login(username='test', password='12345')
        response = self.client.post(
            reverse('delete_booking', args=[self.booking.booking_id])
        )
        self.assertRedirects(response, reverse('my_bookings'))
        self.assertFalse(booking.objects.filter(booking_id=self.booking.booking_id).exists())

    def test_delete_booking_decrements_count(self):
        self.client.login(username='test', password='12345')
        self.assertEqual(booking.objects.filter(user=self.user).count(), 1)
        self.client.post(reverse('delete_booking', args=[self.booking.booking_id]))
        self.assertEqual(booking.objects.filter(user=self.user).count(), 0)

    def test_user_cannot_delete_other_user_booking(self):
        other_booking = booking.objects.create(
            user=self.other_user,
            check_in_date=self.tomorrow,
            check_out_date=self.day_after_tomorrow,
            hotel_type=self.hotel
        )
        self.client.login(username='test', password='12345')
        response = self.client.post(
            reverse('delete_booking', args=[other_booking.booking_id])
        )
        self.assertEqual(response.status_code, 404)
        self.assertTrue(booking.objects.filter(booking_id=other_booking.booking_id).exists())


class EditProfileViewTest(TestCase):
    """Test cases for the edit profile view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='12345')

    def test_edit_profile_page_loads(self):
        self.client.login(username='test', password='12345')
        response = self.client.get(reverse('edit_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'hBooking/edit_profile.html')

    def test_edit_profile_form_in_context(self):
        self.client.login(username='test', password='12345')
        response = self.client.get(reverse('edit_profile'))
        self.assertIn('form', response.context)
        self.assertIn('password_form', response.context)


class UpdateProfileViewTest(TestCase):
    """Test cases for the update profile view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test',
            password='12345',
            email='test@example.com'
        )

    def test_update_profile_valid_email(self):
        self.client.login(username='test', password='12345')
        response = self.client.post(reverse('update_profile'), {
            'username': 'test',
            'email': 'newemail@example.com',
            'old_password': '',
            'new_password1': '',
            'new_password2': ''
        })
        self.assertRedirects(response, reverse('edit_profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'newemail@example.com')

    def test_update_profile_with_password(self):
        self.client.login(username='test', password='12345')
        response = self.client.post(reverse('update_profile'), {
            'username': 'test',
            'email': 'test@example.com',
            'old_password': '12345',
            'new_password1': 'newpassword123',
            'new_password2': 'newpassword123'
        })
        self.assertRedirects(response, reverse('edit_profile'))

    def test_update_profile_password_mismatch(self):
        self.client.login(username='test', password='12345')
        response = self.client.post(reverse('update_profile'), {
            'username': 'test',
            'email': 'test@example.com',
            'old_password': '12345',
            'new_password1': 'newpassword123',
            'new_password2': 'differentpassword'
        })
        self.assertRedirects(response, reverse('edit_profile'))

    def test_update_profile_duplicate_username(self):
        other_user = User.objects.create_user(username='other', password='12345')
        self.client.login(username='test', password='12345')
        response = self.client.post(reverse('update_profile'), {
            'username': 'other',
            'email': 'test@example.com',
            'old_password': '',
            'new_password1': '',
            'new_password2': ''
        })
        # Should return error
        self.assertEqual(response.status_code, 302)