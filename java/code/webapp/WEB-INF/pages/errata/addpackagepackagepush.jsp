<%@ taglib uri="http://rhn.redhat.com/rhn" prefix="rhn" %>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
<%@ taglib uri="http://struts.apache.org/tags-html" prefix="html" %>
<%@ taglib uri="http://struts.apache.org/tags-bean" prefix="bean" %>


<html>
<head>
</head>
<body>
<rhn:toolbar base="h1" icon="header-errata"
	            helpUrl="">
    <bean:message key="errata.publish.toolbar"/> <c:out value="${advisory}" />
  </rhn:toolbar>

  <p><bean:message key="errata.publish.packagepush.description" arg0="${requestScope.channel_name}"/></p>
<c:set var="pageList" value="${requestScope.pageList}" />
<html:form action="/errata/manage/AddPackagePackagePushSubmit">
<rhn:csrf />
<%@ include file="/WEB-INF/pages/common/fragments/errata/packagepush.jspf" %>
<rhn:submitted/>
</html:form>
</body>
</html>
