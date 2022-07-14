# custom report
class custom_report_class(models.AbstractModel):
    _name = 'report.module_name.my_custom_report'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('module_name.my_custom_report')

        model_obj = self.env['cms.schedulerline'].sudo().search([('id', '=', self._ids[0])])

        docargs = {
            'data': model_obj,
        }
        return report_obj.render('module_name.my_custom_report', docargs)

